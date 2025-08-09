# event_logger.py


from datetime import datetime
from typing import Optional, List, Dict, Union
import pandas as pd
import json

from main.enums.report_enums import EventType, DeviceID


class EventLogger:
    def __init__(self, max_entries: int = 100000):
        """
        Inicializa el registro de eventos.
        
        Args:
            max_entries: Límite máximo de eventos a almacenar (para prevenir uso excesivo de memoria)
        """
        self._log = pd.DataFrame(columns=[
            'timestamp',
            'event_type',
            'device_id',
            'device_display_name',
            'new_value',
            'session_id',
            'elapsed_seconds',
            'metadata'
        ])
        self._session_start = None
        self._current_session = 0
        self._max_entries = max_entries
        self._session_metadata = {}

    # === Métodos básicos ===
    def start_session(self, metadata: Optional[dict] = None):
        """
        Inicia una nueva sesión de registro.
        
        Args:
            metadata: Diccionario con metadatos adicionales de la sesión
        """
        self._current_session += 1
        self._session_start = datetime.now()
        self._session_metadata[self._current_session] = metadata or {}
        
        self._add_event(
            event_type=EventType.SESSION_START,
            device_id=DeviceID.SYSTEM,
            value=f"Sesión {self._current_session}",
            metadata=metadata
        )

    def end_session(self):
        """Finaliza la sesión actual"""
        if self._session_start:
            self._add_event(
                event_type=EventType.SESSION_END,
                device_id=DeviceID.SYSTEM,
                value=f"Duración: {self.get_current_session_duration():.2f}s"
            )
            self._session_start = None

    def log_event(self, 
                 event_type: EventType, 
                 device_id: DeviceID, 
                 value: Union[str, int, float, bool],
                 metadata: Optional[dict] = None):
        """
        Registra un evento en el log.
        
        Args:
            event_type: Tipo de evento (de EventType)
            device_id: Dispositivo relacionado (de DeviceID)
            value: Valor asociado al evento
            metadata: Diccionario con metadatos adicionales
        """
        self._add_event(event_type, device_id, value, metadata)

    def _add_event(self, 
                  event_type: EventType, 
                  device_id: DeviceID, 
                  value: Union[str, int, float, bool],
                  metadata: Optional[dict] = None):
        """Añade un nuevo evento al DataFrame interno"""
        now = datetime.now()
        elapsed = (now - self._session_start).total_seconds() if self._session_start else 0.0
        
        new_entry = {
            'timestamp': now,
            'event_type': event_type.name,
            'device_id': device_id.name,
            'device_display_name': device_id.value,
            'new_value': value,
            'session_id': self._current_session,
            'elapsed_seconds': round(elapsed, 3),
            'metadata': json.dumps(metadata) if metadata else None
        }
        
        self._log = pd.concat([
            self._log,
            pd.DataFrame([new_entry])
        ], ignore_index=True)
        
        # Auto-limpiar si excede el máximo
        if len(self._log) > self._max_entries:
            self._log = self._log.iloc[-self._max_entries:]

    # === Métodos de consulta ===
    def get_current_session_duration(self) -> float:
        """Devuelve la duración actual de la sesión en segundos"""
        if not self._session_start:
            return 0.0
        return (datetime.now() - self._session_start).total_seconds()

    def get_session_ids(self) -> List[int]:
        """Devuelve lista de IDs de sesión registrados"""
        return sorted(self._log['session_id'].unique())

    def get_event_types(self) -> List[str]:
        """Devuelve lista de tipos de evento registrados"""
        return sorted(self._log['event_type'].unique())

    def get_device_ids(self) -> List[str]:
        """Devuelve lista de IDs de dispositivo registrados"""
        return sorted(self._log['device_id'].unique())

    # === Métodos de filtrado ===
    def filter_events(self,
                    event_types: Optional[List[EventType]] = None,
                    devices: Optional[List[DeviceID]] = None,
                    sessions: Optional[List[int]] = None,
                    time_range: Optional[tuple] = None,
                    min_elapsed: Optional[float] = None,
                    max_elapsed: Optional[float] = None,
                    include_metadata: bool = False) -> pd.DataFrame:
        """
        Filtra eventos con múltiples criterios.
        
        Args:
            event_types: Lista de tipos de evento a incluir
            devices: Lista de dispositivos a incluir
            sessions: Lista de IDs de sesión a incluir
            time_range: Tupla (start, end) como datetime
            min_elapsed: Segundos mínimos desde inicio de sesión
            max_elapsed: Segundos máximos desde inicio de sesión
            include_metadata: Incluir columna de metadatos en el resultado
            
        Returns:
            DataFrame filtrado
        """
        df = self._log.copy()
        
        # Aplicar filtros en cascada
        if event_types:
            df = df[df['event_type'].isin([et.name for et in event_types])]
        if devices:
            df = df[df['device_id'].isin([d.name for d in devices])]
        if sessions:
            df = df[df['session_id'].isin(sessions)]
        if time_range:
            start, end = time_range
            df = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
        if min_elapsed is not None:
            df = df[df['elapsed_seconds'] >= min_elapsed]
        if max_elapsed is not None:
            df = df[df['elapsed_seconds'] <= max_elapsed]
            
        if not include_metadata:
            df = df.drop(columns=['metadata'])
            
        return df.reset_index(drop=True)

    def get_events_by_type(self, event_type: EventType) -> pd.DataFrame:
        """Retorna todos los eventos de un tipo específico"""
        return self.filter_events(event_types=[event_type])

    def get_events_by_device(self, device: DeviceID) -> pd.DataFrame:
        """Retorna todos los eventos de un dispositivo específico"""
        return self.filter_events(devices=[device])

    def get_events_by_session(self, session_id: int) -> pd.DataFrame:
        """Retorna todos los eventos de una sesión específica"""
        return self.filter_events(sessions=[session_id])

    def get_events_by_time_range(self, start: datetime, end: datetime) -> pd.DataFrame:
        """Retorna eventos dentro de un rango temporal"""
        return self.filter_events(time_range=(start, end))

    # === Métodos de exportación ===
    def save_to_file(self, 
                   filename: str, 
                   format: str = 'csv',
                   **filter_kwargs):
        """
        Guarda eventos a archivo.
        
        Args:
            filename: Ruta del archivo
            format: 'csv', 'json', 'parquet' o 'feather'
            **filter_kwargs: Argumentos para filter_events()
        """
        data = self.filter_events(**filter_kwargs)
        
        if format.lower() == 'csv':
            data.to_csv(filename, index=False)
        elif format.lower() == 'json':
            data.to_json(filename, orient='records', indent=2)
        elif format.lower() == 'parquet':
            data.to_parquet(filename)
        elif format.lower() == 'feather':
            data.to_feather(filename)
        else:
            raise ValueError("Formato debe ser 'csv', 'json', 'parquet' o 'feather'")

    def load_from_file(self, filename: str, format: str = 'csv'):
        """
        Carga eventos desde archivo (preserva los existentes).
        
        Args:
            filename: Ruta del archivo
            format: 'csv', 'json', 'parquet' o 'feather'
        """
        if format.lower() == 'csv':
            new_data = pd.read_csv(filename)
        elif format.lower() == 'json':
            new_data = pd.read_json(filename, orient='records')
        elif format.lower() == 'parquet':
            new_data = pd.read_parquet(filename)
        elif format.lower() == 'feather':
            new_data = pd.read_feather(filename)
        else:
            raise ValueError("Formato debe ser 'csv', 'json', 'parquet' o 'feather'")
        
        # Convertir timestamp si es necesario
        if 'timestamp' in new_data and new_data['timestamp'].dtype == object:
            new_data['timestamp'] = pd.to_datetime(new_data['timestamp'])
            
        self._log = pd.concat([self._log, new_data], ignore_index=True)
        
        # Actualizar el ID máximo de sesión
        if 'session_id' in new_data:
            self._current_session = max(self._current_session, new_data['session_id'].max())

    # === Métodos de limpieza ===
    def clear_log(self, confirm: bool = False) -> bool:
        """Limpia completamente el registro"""
        if confirm:
            self._log = pd.DataFrame(columns=self._log.columns)
            self._current_session = 0
            self._session_start = None
            self._session_metadata = {}
            return True
        return False

    def remove_events(self, **filter_kwargs) -> int:
        """
        Elimina eventos que cumplan con los criterios.
        
        Returns:
            Número de eventos eliminados
        """
        original_size = len(self._log)
        filtered = self.filter_events(**filter_kwargs)
        self._log = self._log[~self._log.index.isin(filtered.index)]
        return original_size - len(self._log)

    def get_session_metadata(self, session_id: int) -> dict:
        """Obtiene metadatos almacenados para una sesión específica"""
        return self._session_metadata.get(session_id, {}).copy()