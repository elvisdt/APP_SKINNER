

from datetime import datetime
from enum import Enum, auto
from typing import Optional, Dict, Union, Any
import pandas as pd
import json
import warnings

from PyQt6.QtCore import QObject, pyqtSignal

class EventType(Enum):
    LED_CHANGE = auto()
    LEVER_PRESS = auto()
    FOOD_DISPENSE = auto()
    FOOD_RECOMPENSE = auto()
    SESSION_START = auto()
    SESSION_END = auto()
    SYSTEM_EVENT = auto()


class DeviceID(Enum):
    LED_01 = "LED 01"
    LED_02 = "LED 02"
    LEVER_01 = "Palanca 01"
    LEVER_02 = "Palanca 02"
    DISPENSADOR = "Dispensador"
    RECOMPENSA = "Recompensa"
    SYSTEM = "Sistema"


class EventLogger(QObject):
    
    session_ended = pyqtSignal(int)  # Señal que emite el ID de sesión finalizada
     
     
    def __init__(self, max_entries: int = 100000):
        super().__init__()  # Inicializa QObject
        self._dtypes = {
            'timestamp': 'datetime64[ns]',
            'event_type': 'category',
            'device_id': 'category',
            'new_value': 'object',
            'session_id': 'int32',
            'elapsed_sec': 'float64',
            'metadata': 'object'
        }

        self._log = pd.DataFrame({col: pd.Series(dtype=typ) for col, typ in self._dtypes.items()})
        self._current_session = 0
        self._session_start = None
        self._session_metadata: Dict[int, Dict[str, Any]] = {}
        self._max_entries = max_entries

    # ----------------------------
    # Sesiones
    # ----------------------------
    def start_session(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Inicia una nueva sesión. Si hay una activa, la cierra primero."""
        if self.is_session_active():
            self.end_session()

        self._current_session += 1
        self._session_start = datetime.now()
        self._session_metadata[self._current_session] = metadata or {}

        self._log_event(
            event_type=EventType.SESSION_START,
            device=DeviceID.SYSTEM,
            value=self._current_session,
            metadata=self._session_metadata[self._current_session],
            allow_outside_session=True  # Permitir registrar este evento
        )

    def end_session(self) -> None:
        """Finaliza la sesión actual si está activa."""
        if not self.is_session_active():
            return
        session_id = self._current_session
        duration = (datetime.now() - self._session_start).total_seconds()

        self._log_event(
            event_type=EventType.SESSION_END,
            device=DeviceID.SYSTEM,
            value=f"{duration:.2f}",
            metadata={"duration_sec": duration},
            allow_outside_session=True
        )
        
        # Obtener y procesar datos de la sesión
        session_data = self._process_session_data(session_id, duration)
        
        
        self._session_start = None
        self.session_ended.emit(session_data )
        
    def _process_session_data(self, session_id: int, duration: float) -> dict:
        """Procesa los datos de la sesión para el reporte"""
        events = self.get_events(sessions=[session_id])
        metadata = self.get_session_metadata(session_id)
        
        # Filtrar eventos relevantes
        lever1 = events[
            (events["device_id"] == DeviceID.LEVER_01.name) & 
            (events["event_type"] == EventType.LEVER_PRESS.name)
        ]
        lever2 = events[
            (events["device_id"] == DeviceID.LEVER_02.name) & 
            (events["event_type"] == EventType.LEVER_PRESS.name)
        ]
        rewards = events[
            events["event_type"].isin([EventType.FOOD_DISPENSE.name, EventType.FOOD_RECOMPENSE.name])
        ]
        led_changes = events[
            events["device_id"].str.startswith("LED_") & 
            (events["event_type"] == EventType.LED_CHANGE.name)
        ]
        
        return {
            "session_id": session_id,
            "duration": duration,
            "metadata": metadata,
            "lever1_presses": lever1["new_value"].tolist(),
            "lever1_times": lever1["elapsed_sec"].astype(float).tolist(),
            "lever2_presses": lever2["new_value"].tolist(),
            "lever2_times": lever2["elapsed_sec"].astype(float).tolist(),
            "reward_times": rewards["elapsed_sec"].astype(float).tolist(),
            "led_changes": led_changes[["device_id", "elapsed_sec", "new_value"]].to_dict('records'),
            "raw_events": events  # Datos crudos por si acaso
        }
        
    def is_session_active(self) -> bool:
        return self._session_start is not None

    def get_current_session_id(self) -> int:
        return self._current_session

    def get_session_metadata(self, session_id: int) -> Dict[str, Any]:
        return self._session_metadata.get(session_id, {})

    # ----------------------------
    # Registro de eventos
    # ----------------------------
    def log_event(
        self,
        event_type: EventType,
        device: DeviceID,
        value: Union[str, int, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Registra un evento, solo si hay sesión activa."""
        self._log_event(event_type, device, value, metadata)

    def _log_event(
        self,
        event_type: EventType,
        device: DeviceID,
        value: Union[str, int, float],
        metadata: Optional[Dict[str, Any]] = None,
        allow_outside_session: bool = False
    ) -> None:
        """Método interno para registrar eventos."""
        if not self.is_session_active() and not allow_outside_session:
            raise RuntimeError(f"No hay sesión activa para registrar evento: {event_type.name}")

        now = datetime.now()
        elapsed = (now - self._session_start).total_seconds() if self.is_session_active() else 0.0

        new_entry = {
            'timestamp': pd.to_datetime(now),
            'event_type': event_type.name,
            'device_id': device.name,
            'new_value': str(value),
            'session_id': self._current_session,
            'elapsed_sec': round(float(elapsed), 3),
            'metadata': json.dumps(metadata) if metadata else None
        }

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)

            new_df = pd.DataFrame([new_entry]).astype({
                'timestamp': 'datetime64[ns]',
                'event_type': 'category',
                'device_id': 'category'
            })

            self._log = pd.concat([self._log, new_df], ignore_index=True).astype(self._dtypes)

        if len(self._log) > self._max_entries:
            self._log = self._log.iloc[-self._max_entries:]

    # ----------------------------
    # Consultas y exportación
    # ----------------------------
    def get_events(self, **filters) -> pd.DataFrame:
        df = self._log.copy()

        if 'event_types' in filters:
            event_names = [et.name for et in filters['event_types']]
            df = df[df['event_type'].isin(event_names)]

        if 'devices' in filters:
            device_names = [d.name for d in filters['devices']]
            df = df[df['device_id'].isin(device_names)]

        if 'sessions' in filters:
            df = df[df['session_id'].isin(filters['sessions'])]

        return df

    def get_last_event(self, session_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if session_id is None:
            session_id = self._current_session

        df_session = self._log[self._log["session_id"] == session_id]
        if df_session.empty:
            return None

        return df_session.iloc[-1].to_dict()

    def save_to_csv(self, filename: str) -> None:
        self._log.to_csv(filename, index=False)

    def clear_log(self) -> None:
        self._log = pd.DataFrame({col: pd.Series(dtype=typ) for col, typ in self._dtypes.items()})
        self._current_session = 0
        self._session_start = None
        self._session_metadata = {}
