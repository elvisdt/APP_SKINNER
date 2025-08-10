# from datetime import datetime
# from enum import Enum, auto
# import pandas as pd
# from typing import Optional, List, Dict, Union
# import json

# class EventType(Enum):
#     LED_CHANGE = auto()
#     LEVER_PRESS = auto()
#     FOOD_DISPENSE = auto()
#     SESSION_START = auto()
#     SESSION_END = auto()
#     SYSTEM_EVENT = auto()

# class DeviceID(Enum):
#     LED_01 = "LED 01"
#     LED_02 = "LED 02"
#     LEVER_01 = "Palanca 01"
#     LEVER_02 = "Palanca 02"
#     FOOD_DEVICE = "Dispensador"
#     SYSTEM = "Sistema"

# class EventLogger:
#     def __init__(self, max_entries: int = 100000):
#         self._log = pd.DataFrame(columns=[
#             'timestamp', 'event_type', 'device_id', 'device_name',
#             'new_value', 'session_id', 'elapsed_sec', 'metadata'
#         ])
#         self._current_session = 0
#         self._session_start = None
#         self._max_entries = max_entries
#         self._session_metadata = {}

#     def start_session(self, metadata: Optional[dict] = None):
#         self._current_session += 1
#         self._session_start = datetime.now()
#         self._session_metadata[self._current_session] = metadata or {}
#         self._log_event(EventType.SESSION_START, DeviceID.SYSTEM, f"Sesión {self._current_session}")

#     def end_session(self):
#         if self._session_start:
#             duration = (datetime.now() - self._session_start).total_seconds()
#             self._log_event(EventType.SESSION_END, DeviceID.SYSTEM, f"Duración: {duration:.2f}s")
#             self._session_start = None

#     def log_event(self, event_type: EventType, device: DeviceID, value: Union[str, int, float], metadata: Optional[dict] = None):
#         self._log_event(event_type, device, value, metadata)

#     # def _log_event(self, event_type: EventType, device: DeviceID, value: Union[str, int, float], metadata: Optional[dict] = None):
#     #     now = datetime.now()
#     #     elapsed = (now - self._session_start).total_seconds() if self._session_start else 0.0
        
#     #     new_entry = {
#     #         'timestamp': now,
#     #         'event_type': event_type.name,
#     #         'device_id': device.name,
#     #         'device_name': device.value,
#     #         'new_value': value,
#     #         'session_id': self._current_session,
#     #         'elapsed_sec': round(elapsed, 3),
#     #         'metadata': json.dumps(metadata) if metadata else None
#     #     }
        
#     #     self._log = pd.concat([self._log, pd.DataFrame([new_entry])], ignore_index=True)
        
#     #     if len(self._log) > self._max_entries:
#     #         self._log = self._log.iloc[-self._max_entries:]

#     def _log_event(self, event_type: EventType, device: DeviceID, value: Union[str, int, float], metadata: Optional[dict] = None):
#         now = datetime.now()
#         elapsed = (now - self._session_start).total_seconds() if self._session_start else 0.0
        
#         # Definir estructura completa del registro
#         new_entry = {
#             'timestamp': now,
#             'event_type': event_type.name,
#             'device_id': device.name,
#             'device_name': device.value,
#             'new_value': value,
#             'session_id': self._current_session,
#             'elapsed_sec': round(elapsed, 3),
#             'metadata': json.dumps(metadata) if metadata else None
#         }
        
#         # Crear DataFrame asegurando todas las columnas
#         columns = self._log.columns
#         new_df = pd.DataFrame([new_entry], columns=columns)
        
#         # Concatenar
#         self._log = pd.concat([self._log, new_df], ignore_index=True)
        
#         if len(self._log) > self._max_entries:
#             self._log = self._log.iloc[-self._max_entries:]
            
#     def get_events(self, **filters) -> pd.DataFrame:
#         df = self._log.copy()
#         if 'event_types' in filters:
#             df = df[df['event_type'].isin([et.name for et in filters['event_types']])]
#         if 'devices' in filters:
#             df = df[df['device_id'].isin([d.name for d in filters['devices']])]
#         if 'sessions' in filters:
#             df = df[df['session_id'].isin(filters['sessions'])]
#         return df

#     def save_to_csv(self, filename: str):
#         self._log.to_csv(filename, index=False)



from datetime import datetime
from enum import Enum, auto
import pandas as pd
from typing import Optional, Dict, Union, Any
import json
import warnings

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
    RECOMPENSA = "REcompensa"
    SYSTEM = "Sistema"

class EventLogger:
    def __init__(self, max_entries: int = 100000):
        # Definir estructura de columnas con tipos de datos explícitos
        self._dtypes = {
            'timestamp': 'datetime64[ns]',
            'event_type': 'category',
            'device_id': 'category',
            'device_name': 'object',
            'new_value': 'object',
            'session_id': 'int32',
            'elapsed_sec': 'float64',
            'metadata': 'object'
        }
        
        # Inicializar DataFrame con tipos de datos definidos
        self._log = pd.DataFrame({col: pd.Series(dtype=typ) 
                                for col, typ in self._dtypes.items()})
        
        self._current_session = 0
        self._session_start = None
        self._max_entries = max_entries
        self._session_metadata = {}

    def start_session(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Inicia una nueva sesión de registro."""
        self._current_session += 1
        self._session_start = datetime.now()
        self._session_metadata[self._current_session] = metadata or {}
        self._log_event(
            event_type=EventType.SESSION_START,
            device=DeviceID.SYSTEM,
            value=f"Sesión {self._current_session}",
            metadata=self._session_metadata[self._current_session]
        )

    def end_session(self) -> None:
        """Finaliza la sesión actual."""
        if self._session_start:
            duration = (datetime.now() - self._session_start).total_seconds()
            self._log_event(
                event_type=EventType.SESSION_END,
                device=DeviceID.SYSTEM,
                value=f"Duración: {duration:.2f}s",
                metadata={"duration_sec": duration}
            )
            self._session_start = None

    def log_event(
        self,
        event_type: EventType,
        device: DeviceID,
        value: Union[str, int, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Registra un evento en el logger."""
        self._log_event(event_type, device, value, metadata)

    def _log_event(
        self,
        event_type: EventType,
        device: DeviceID,
        value: Union[str, int, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Método interno para registrar eventos."""
        now = datetime.now()
        elapsed = (now - self._session_start).total_seconds() if self._session_start else 0.0
        
        # Crear nueva entrada con tipos de datos consistentes
        new_entry = {
            'timestamp': pd.to_datetime(now),
            'event_type': event_type.name,
            'device_id': device.name,
            'device_name': device.value,
            'new_value': str(value),  # Convertir a string para consistencia
            'session_id': self._current_session,
            'elapsed_sec': round(float(elapsed), 3),
            'metadata': json.dumps(metadata) if metadata else None
        }
        
        # Suprimir warnings específicos de concatenación
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            
            # Convertir a DataFrame con tipos definidos
            new_df = pd.DataFrame([new_entry]).astype({
                'timestamp': 'datetime64[ns]',
                'event_type': 'category',
                'device_id': 'category'
            })
            
            # Concatenar asegurando tipos de datos
            self._log = pd.concat([
                self._log, 
                new_df
            ], ignore_index=True).astype(self._dtypes)
        
        # Mantener tamaño máximo
        if len(self._log) > self._max_entries:
            self._log = self._log.iloc[-self._max_entries:]

    def get_events(self, **filters) -> pd.DataFrame:
        """Obtiene eventos filtrados."""
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

    def save_to_csv(self, filename: str) -> None:
        """Guarda los registros en un archivo CSV."""
        self._log.to_csv(filename, index=False)

    def get_session_metadata(self, session_id: int) -> Dict[str, Any]:
        """Obtiene los metadatos de una sesión específica."""
        return self._session_metadata.get(session_id, {})

    def clear_log(self) -> None:
        """Limpia todos los registros y reinicia el logger."""
        self._log = pd.DataFrame({col: pd.Series(dtype=typ) 
                               for col, typ in self._dtypes.items()})
        self._current_session = 0
        self._session_start = None
        self._session_metadata = {}