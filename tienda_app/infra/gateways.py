import datetime
from ..domain.interfaces import ProcesadorPago

import datetime


class BancoNacionalProcesador(ProcesadorPago):
    def pagar(self, monto: float) -> bool:
        # SUSTITUYE "TU_NOMBRE" por tu nombre real
        archivo_log = "pagos_locales_Julian_Lara_Aristizabal.log"

        with open(archivo_log, "a") as f:
            f.write(f"[{datetime.datetime.now()}] Transaccion exitosa por: ${monto}\n")

        return True
    

