# utils/timer.py
# Utilidad de temporización de alta precisión para medir la ejecución
# de los algoritmos de búsqueda en milisegundos.

import time
from typing import Callable, Any, Tuple


class Timer:
    """
    Temporizador de contexto para medir bloques de código.

    Uso como context manager:
        with Timer() as t:
            run_algorithm()
        print(t.elapsed_ms)  # tiempo en ms

    Uso como decorador funcional:
        elapsed, result = Timer.measure(fn, *args, **kwargs)
    """

    def __init__(self) -> None:
        self._start: float = 0.0
        self._end: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_) -> None:
        self._end = time.perf_counter()

    @property
    def elapsed_ms(self) -> float:
        """Tiempo transcurrido en milisegundos."""
        return (self._end - self._start) * 1_000

    @staticmethod
    def measure(fn: Callable, *args, **kwargs) -> Tuple[float, Any]:
        """
        Ejecuta `fn(*args, **kwargs)` y retorna (elapsed_ms, result).

        Args:
            fn: Función a medir.
            *args: Argumentos posicionales para fn.
            **kwargs: Argumentos de palabra clave para fn.

        Returns:
            Tupla (tiempo_en_ms: float, resultado: Any).
        """
        t = Timer()
        with t:
            result = fn(*args, **kwargs)
        return t.elapsed_ms, result