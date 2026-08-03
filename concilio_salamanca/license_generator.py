from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


BIG_MAC_INDEX: Dict[str, float] = {
    "US": 5.69,
    "CH": 7.73,
    "NO": 7.14,
    "SE": 5.84,
    "DK": 5.67,
    "IL": 5.34,
    "CA": 5.27,
    "AU": 5.07,
    "NZ": 4.88,
    "GB": 4.82,
    "KR": 4.43,
    "AE": 4.39,
    "JP": 4.35,
    "DE": 4.25,
    "FR": 4.20,
    "IT": 4.15,
    "ES": 3.95,
    "PT": 3.72,
    "GR": 3.68,
    "PL": 3.45,
    "CZ": 3.42,
    "HU": 3.35,
    "RO": 3.28,
    "CL": 3.75,
    "BR": 4.25,
    "AR": 3.15,
    "CO": 3.48,
    "PE": 3.25,
    "MX": 3.19,
    "CR": 4.10,
    "PA": 3.90,
    "DO": 3.55,
    "GT": 3.50,
    "EC": 3.40,
    "PY": 3.30,
    "BO": 3.20,
    "UY": 4.80,
    "ZA": 3.10,
    "EG": 2.55,
    "NG": 2.40,
    "KE": 2.30,
    "ET": 2.10,
    "IN": 2.39,
    "CN": 3.25,
    "TH": 3.05,
    "VN": 2.85,
    "ID": 2.55,
    "PH": 2.60,
    "PK": 2.10,
    "BD": 2.05,
    "MM": 2.00,
    "RU": 2.95,
    "TR": 2.80,
    "UA": 2.15,
    "SG": 4.90,
    "HK": 4.85,
    "TW": 4.40,
    "MY": 2.85,
}

RENT_RATIO: Dict[str, float] = {
    "US": 0.35,
    "CH": 0.38,
    "NO": 0.35,
    "SE": 0.33,
    "DK": 0.34,
    "GB": 0.36,
    "DE": 0.32,
    "FR": 0.30,
    "IT": 0.28,
    "ES": 0.30,
    "PT": 0.28,
    "GR": 0.26,
    "PL": 0.28,
    "CZ": 0.30,
    "HU": 0.26,
    "RO": 0.24,
    "AU": 0.33,
    "NZ": 0.32,
    "CA": 0.34,
    "JP": 0.30,
    "KR": 0.28,
    "SG": 0.32,
    "HK": 0.38,
    "TW": 0.26,
    "CN": 0.28,
    "IN": 0.22,
    "BR": 0.25,
    "MX": 0.24,
    "AR": 0.26,
    "CO": 0.24,
    "CL": 0.24,
    "PE": 0.22,
    "ZA": 0.23,
    "NG": 0.30,
    "KE": 0.28,
    "EG": 0.24,
    "TH": 0.22,
    "VN": 0.20,
    "ID": 0.22,
    "PH": 0.25,
    "PK": 0.20,
    "BD": 0.18,
    "TR": 0.24,
    "RU": 0.22,
    "UA": 0.20,
}

FOOD_RATIO: Dict[str, float] = {
    "US": 0.12,
    "CH": 0.14,
    "NO": 0.13,
    "SE": 0.12,
    "DK": 0.12,
    "GB": 0.11,
    "DE": 0.11,
    "FR": 0.13,
    "IT": 0.13,
    "ES": 0.12,
    "PT": 0.13,
    "GR": 0.12,
    "PL": 0.15,
    "CZ": 0.14,
    "HU": 0.14,
    "RO": 0.16,
    "AU": 0.11,
    "NZ": 0.12,
    "CA": 0.11,
    "JP": 0.12,
    "KR": 0.12,
    "SG": 0.11,
    "HK": 0.12,
    "TW": 0.11,
    "CN": 0.15,
    "IN": 0.18,
    "BR": 0.14,
    "MX": 0.15,
    "AR": 0.16,
    "CO": 0.15,
    "CL": 0.14,
    "PE": 0.16,
    "ZA": 0.14,
    "NG": 0.25,
    "KE": 0.24,
    "EG": 0.18,
    "TH": 0.16,
    "VN": 0.18,
    "ID": 0.18,
    "PH": 0.20,
    "PK": 0.20,
    "BD": 0.22,
    "TR": 0.16,
    "RU": 0.16,
    "UA": 0.18,
}

TAX_ESTIMATES: Dict[str, float] = {
    "US": 0.24,
    "CH": 0.22,
    "NO": 0.30,
    "SE": 0.32,
    "DK": 0.36,
    "GB": 0.25,
    "DE": 0.30,
    "FR": 0.28,
    "IT": 0.30,
    "ES": 0.24,
    "PT": 0.25,
    "GR": 0.24,
    "PL": 0.18,
    "CZ": 0.16,
    "HU": 0.15,
    "RO": 0.10,
    "AU": 0.27,
    "NZ": 0.24,
    "CA": 0.26,
    "JP": 0.23,
    "KR": 0.17,
    "SG": 0.10,
    "HK": 0.10,
    "TW": 0.12,
    "CN": 0.15,
    "IN": 0.13,
    "BR": 0.17,
    "MX": 0.16,
    "AR": 0.20,
    "CO": 0.15,
    "CL": 0.15,
    "PE": 0.12,
    "ZA": 0.22,
    "NG": 0.10,
    "KE": 0.14,
    "EG": 0.10,
    "TH": 0.10,
    "VN": 0.10,
    "ID": 0.10,
    "PH": 0.10,
    "PK": 0.05,
    "BD": 0.07,
    "TR": 0.15,
    "RU": 0.13,
    "UA": 0.12,
}

DEFAULT_BIG_MAC = 3.50
DEFAULT_RENT = 0.30
DEFAULT_FOOD = 0.14
DEFAULT_TAX = 0.15

BME_BRACKETS = [
    (500, 0.00, "Gratis (solo Auto-Favorito)"),
    (2000, 0.01, "1% del ingreso bruto atribuible"),
    (5000, 0.03, "3% del ingreso bruto atribuible"),
    (10000, 0.05, "5% del ingreso bruto atribuible"),
    (float("inf"), 0.10, "10% del ingreso bruto atribuible"),
]

# Tabla plana de precios corporativos (alternativa simplificada al BME)
# Una empresa puede optar por esta tabla O por el sistema BME, el que sea menor.
FLAT_PRICE_TABLE: list = [
    (0, 100_000, 0, "Open Source gratuito"),
    (100_000, 1_000_000, 500, "Licencia Individual/Startup"),
    (1_000_000, 10_000_000, 2_500, "Licencia PYME"),
    (10_000_000, 100_000_000, 10_000, "Licencia Corporativa"),
    (100_000_000, 1_000_000_000, 50_000, "Licencia Enterprise"),
    (1_000_000_000, float("inf"), 0.001, "Licencia Oligarca (0.1% facturacion anual, min $100K)"),
]

# Cuota de sostenimiento para proyectos huerfanos
ORPHAN_FUND_RATE = 0.05  # 5% de cada licencia va al Fondo de Sostenibilidad

# Diezmo Comercial sin Compliance (Art. 4.0)
# Empresas que usan RNS en VM privadas, SaaS o backend sin contrato de compliance
FLAT_PRICE_COMMERCIAL_NO_COMPLIANCE: list = [
    (0, 1_000_000, 0.005, "0.5% del Margen Bruto Operativo"),
    (1_000_000, 10_000_000, 0.01, "1% del Margen Bruto Operativo"),
    (10_000_000, 100_000_000, 0.02, "2% del Margen Bruto Operativo"),
    (100_000_000, float("inf"), 0.03, "3% del Margen Bruto Operativo"),
]

# FRN Orphan Fund rate
ORPHAN_FUND_RATE_COMMERCIAL = 0.05  # 5% de cada pago comercial al Fondo


class BigMacCalculator:
    @staticmethod
    def big_mac_price(country: str) -> float:
        return BIG_MAC_INDEX.get(country.upper(), DEFAULT_BIG_MAC)

    @staticmethod
    def disposable_income_bme(
        monthly_income_usd: float,
        residence_country: str,
        income_country: Optional[str] = None,
    ) -> float:
        res = residence_country.upper()
        big_mac = BigMacCalculator.big_mac_price(res)
        rent_r = RENT_RATIO.get(res, DEFAULT_RENT)
        food_r = FOOD_RATIO.get(res, DEFAULT_FOOD)
        tax_r = TAX_ESTIMATES.get(res, DEFAULT_TAX)

        costs = monthly_income_usd * (rent_r + food_r + tax_r)
        disposable = max(monthly_income_usd - costs, 0)
        return disposable / big_mac if big_mac > 0 else 0

    @staticmethod
    def get_tax_bracket(bme: float) -> tuple:
        for threshold, rate, label in BME_BRACKETS:
            if bme < threshold:
                return (rate, label, bme)
        return (0.10, BME_BRACKETS[-1][2], bme)


class LicenseGenerator:
    BASE_THRESHOLD_USD = 1_000_000
    BASE_SME_THRESHOLD_USD = 250_000
    BASE_NONPROFIT_THRESHOLD_USD = 100_000
    POOR_DEV_THRESHOLD_MXN = 20_000

    def __init__(
        self,
        developer_name: str = "",
        project_name: str = "",
        github_repo: str = "",
        jubilee_year: Optional[int] = None,
        std_version: bool = False,
    ):
        self.developer_name = developer_name
        self.project_name = project_name
        self.github_repo = github_repo
        self.jubilee_year = jubilee_year
        self.std_version = std_version

    def get_localized_thresholds(self, country_code: str) -> Dict:
        factor = 1.0
        if country_code.upper() in BIG_MAC_INDEX:
            factor = BIG_MAC_INDEX[country_code.upper()] / BIG_MAC_INDEX.get("US", 5.69)
        factor = max(factor, 0.3)

        bm_price_usd = BIG_MAC_INDEX.get(country_code.upper(), DEFAULT_BIG_MAC)
        poor_dev_usd = (self.POOR_DEV_THRESHOLD_MXN / 55) * (
            bm_price_usd / BIG_MAC_INDEX.get("MX", 3.19)
        )

        bme_brackets_display = []
        for threshold, rate, label in BME_BRACKETS:
            bme_in_usd = threshold * bm_price_usd
            bme_brackets_display.append(
                {
                    "bme": threshold,
                    "tasa": f"{rate * 100:.0f}%",
                    "equivalente_usd_mensual": f"${bme_in_usd:,.0f}",
                    "label": label,
                }
            )

        return {
            "ingresos_brutos_alto": self.BASE_THRESHOLD_USD * factor,
            "ingresos_brutos_pyme": self.BASE_SME_THRESHOLD_USD * factor,
            "nonprofit_max": self.BASE_NONPROFIT_THRESHOLD_USD * factor,
            "poor_dev_usd": poor_dev_usd,
            "big_mac_price_usd": bm_price_usd,
            "bme_brackets": bme_brackets_display,
            "ppa_factor": factor,
        }

    def generate_license(self, country_code: str = "US") -> str:
        t = self.get_localized_thresholds(country_code)
        bm_price = t["big_mac_price_usd"]
        brackets = t["bme_brackets"]

        brackets_text = ""
        for b in brackets:
            brackets_text += (
                f"  - Hasta {b['bme']} BME (~${b['equivalente_usd_mensual']}/mes "
                f"en {country_code.upper()}): **{b['label']}**\n"
            )

                # STD header badge
        std_tag = " [VERSION STD]" if self.std_version else ""
        next_jubilee_year = datetime.now().year + 7
        return f"""# RERUM NOVARUM STATUTO (RNS) v5.0{std_tag}
## *Open To Open Source, Closed to Oligarchs*
## *El trabajador merece su salario*

### Fuentes Doctrinales
Este Statuto se fundamenta en las siguientes fuentes de Derecho Natural y Doctrina Social:

| Fuente | Principio Rector | Aplicacion en el Statuto |
|--------|------------------|--------------------------|
| **Decalogo (Exodo 20:1-17)** | VII: No robaras. X: No codiciaras los bienes ajenos. | La extraccion de valor del trabajo ajeno sin retribucion constituye violacion del Septimo Mandamiento. La codicia de explotar el commons sin retorno viola el Decimo. |
| **Rerum Novarum (Leon XIII, 1891)** | El trabajo no es una mercancia. El salario justo debe permitir vivir dignamente. | Articulos 3 (Salario no limosna), 4 (Diezmo Tecnologico), 9 (No-Soporte sin pago). |
| **Quadragesimo Anno (Pio XI, 1931)** | Principio de subsidiariedad: las decisiones deben tomarse al nivel mas local posible. | Articulo 12 (Gobernanza STD por consenso comunitario local). |
| **Centesimus Annus (Juan Pablo II, 1991)** | El destino universal de los bienes limita la propiedad privada. | Articulo 11 (Liberacion por Abandono), Articulo 10 (Jubileo del Codigo). |
| **Laborem Exercens (Juan Pablo II, 1981)** | El trabajo es la clave de la cuestion social. El salario es la retribucion debida. | Preambulo (Salario no limosna), Articulo 3.2 (Opciones de contratacion). |
| **Escuela de Salamanca (Vitoria, Soto, Molina)** | Precio justo, bien comun, derecho de gentes, condena de la usura. | Sistema BME de precio justo, Fondo de Sostenibilidad, clausula Anti-Usura. |
| **Compendio de Doctrina Social de la Iglesia (2004)** | La economia debe estar al servicio de la persona, no al reves. | Articulo 5 (Anti-Parasitaria), Articulo 14 (Gobernanza con sede en el Sur Global). |

---

**Preambulo: Del Salario, no de la Limosna**

> *"El trabajador merece su salario"* (Lucas 10:7)
> *"No retendras el salario del jornalero en tu casa hasta la manana"* (Levitico 19:13)
> *"Amos, haced lo que es justo y recto con vuestros siervos, sabiendo que tambien
>  vosotros teneis un Amo en los cielos"* (Colosenses 4:1)
> *"No pondras bozal al buey cuando trillare"* (Deuteronomio 25:4)
> *"No robaras. No codiciaras los bienes de tu projimo."* (Exodo 20:15,17)

El codigo de *software* no es una abstraccion eterea ni un "recurso" a extraer:
es el producto directo del tiempo, el intelecto y el sostenimiento vital de un
trabajador humano. Quien usa este trabajo para generar valor economico debe retribuir
al trabajador que lo sostiene, no con limosna simbolica, sino con **salario justo**
o **porcentaje legitimo de usufructo**.

El **Decalogo** (Exodo 20:1-17) establece en su Septimo Mandamiento *"No robaras"*
y en el Decimo *"No codiciaras los bienes de tu projimo"*. Extraer valor del trabajo
de mantenedores sin retribucion no es "eficiencia de mercado": es violacion de la
Ley Natural. La **Doctrina Social de la Iglesia** (Rerum Novarum, Quadragesimo Anno,
Centesimus Annus, Laborem Exercens) desarrolla estos principios en el magisterio
social: el trabajo tiene primacia sobre el capital, el salario debe ser justo, y el
destino universal de los bienes limita la propiedad privada absoluta. Este Statuto
es la implementacion tecnica de esas fuentes en el dominio del software.

Esta es la diferencia entre la Cooperacion y la Extraccion:
- **Cooperacion**: Pagas salario o % de usufructo, y recibes soporte, garantia y compliance.
- **Extraccion**: Usas sin retribuir, y no recibes soporte, ni garantia, ni compliance.

**Si no se remunera, no hay compliance. Si no hay compliance, no se exige soporte.**
El software libre no es software esclavo.

---

### 0. Estructura del Statuto

| Articulo | Materia |
|----------|---------|
| 1 | Definiciones y Metricas |
| 2 | Libertades Concedidas (Open Source) |
| 3 | Regimen de Propiedad Privada (Salario, Bulas y Excepciones) |
| 4 | Deber de Retribucion (Diezmo: 0-3% sin Compliance, 1-10% con Compliance) |
| 5 | Auditoria, Cumplimiento, Recompensas y Derivative Work |
| 6 | Clausula Anti-Parasitaria |
| 7 | Retroactividad (Modelo WinRAR) |
| 8 | Excomunion Digital |
| 9 | Compatibilidad |
| 10 | No-Remuneracion = No-Soporte |
| 11 | Del Jubileo del Codigo (7 Ano) |
| 12 | De la Liberacion por Abandono |
| 13 | De la Gobernanza STD |
| 14 | De las Bulas (Propiedad Privada Temporal) |
| 15 | Gobernanza del Statuto (Fundacion RNS) |
| 16 | Mediacion y Resolucion de Disputas |
| 17 | Disposiciones Finales |

---

### 1. Definiciones y Metricas

- **"Software"**: El programa, biblioteca o codigo objeto de este Statuto, incluyendo
  codigo fuente y binarios.
- **"Desarrollador"**: {self.developer_name or "[Nombre del desarrollador]"}, titular
  de los derechos de autor del Software.
- **"Proyecto"**: {self.project_name or "[Nombre del proyecto]"}.
- **"Usuario"**: Cualquier persona o entidad que use, modifique o distribuya el Software.
- **"Big Mac Equivalent (BME)"**: Unidad de medida del poder adquisitivo real. Un BME
  equivale al precio de una Big Mac en el pais de residencia del Usuario.
  Precio de referencia en {country_code.upper()}: ${bm_price:.2f} USD = 1 BME.
- **"Kilowatt Equivalent (kWE)"**: Metrica alternativa de poder adquisitivo medida en
  kilovatios-hora (kWh) que un salario minimo puede adquirir. 1 kWE = 1 kWh al precio
  industrial local. El umbral de pobreza se fija en **salario minimo G20 x 3 en kWE**.
  (Articulo 3.4).
- **"Bula"**: Licencia de propiedad privada temporal sobre el Software, adquirible
  por un periodo maximo de 7 anos. Una Bula permite mantener el codigo cerrado
  (fuente no publicada) durante ese periodo. Solo se puede adquirir **UNA Bula
  por proyecto** en toda su historia.
- **"Ingreso Disponible Mensual"**: Ingreso bruto mensual del Usuario, menos:
  - Renta promedio local (~{RENT_RATIO.get(country_code.upper(), 0.30) * 100:.0f}% del ingreso en {country_code.upper()})
  - Alimentacion basica (~{FOOD_RATIO.get(country_code.upper(), 0.14) * 100:.0f}% del ingreso en {country_code.upper()})
  - Impuestos estimados (~{TAX_ESTIMATES.get(country_code.upper(), 0.15) * 100:.0f}% del ingreso en {country_code.upper()})
- **"Margen Bruto Operativo"**: Ingresos directos atribuibles al Software, MENOS:
  - Costos de hardware existente (servidores, almacenamiento, ancho de banda).
  - Costos de personal humano directamente vinculado.
  - Costos de licencias de terceros necesarias para la operacion.
  NO SE DEDUCEN: inversiones en escalabilidad (nuevos servidores, expansion de
  infraestructura), costos de adquisicion de usuarios, ni gastos financieros.
  Esto evita la **estrategia Jeff Bezos** (declarar perdidas operativas eternas
  mientras se extrae valor real).
- **"PYME"**: Empresa con menos de 100 empleados y ventas anuales inferiores a
  ${t["ingresos_brutos_pyme"]:,.0f} USD (ajustado segun PPA local).
- **"Oligarca Tecnologico"**: Entidad con valor de mercado superior a $1,000M USD,
  o que extrae mas de $100M USD anuales de software de codigo abierto sin retribuir
  proporcionalmente a los mantenedores.
- **"Fondo de Sostenibilidad"**: Fondo comunitario alimentado por Bulas, Diezmos y
  multas, destinado a pagar salarios de mantenedores de infraestructura critica
  (Tailwind, Linux Foundation, kernel, compiladores, etc.)
- **"Uso Comercial sin Compliance"**: Situacion donde el Software se ejecuta en:
  . Maquinas virtuales 100% privadas (sin fork publico en GitHub),
  . Backend SaaS (el software corre en servidores del Usuario ofreciendo servicio a terceros),
  . Infraestructura operativa no publica (CI/CD, monitoreo, procesamiento de datos).
  En estos casos, el Usuario paga el Diezmo Comercial simplificado (Articulo 4.0),
  auto-declarado, sin necesidad de contrato de compliance.
- **"Derivative Work sin Fork (Montaje de Software)"**: Modificacion, extension o
  construccion de una obra derivada del Software sin haber realizado un fork publico
  en GitHub o GitLab y sin haber notificado al Autor. Constituye violacion del
  Articulo 5.4 y del Septimo Mandamiento (Exodo 20:15). Sancion: recargo del 50%
  sobre el Diezmo correspondiente + inhabilitacion para Bulas por 7 anos.

**1.1 Prorrateo por Importancia, no por Lineas de Codigo**
La obligacion de retribucion se determina por la **importancia del componente RNS**
en el producto final, no por el porcentaje de lineas de codigo. Si el componente RNS
es critico para la funcionalidad del producto (ej: algoritmo central, modulo de
seguridad, middleware de autenticacion), se paga el **100% del diezmo** aunque el
componente represente solo el 1% del codigo total. Si es accesorio, se prorratea
segun acuerdo entre las partes.

### 2. Libertades Concedidas (Open Source)

Se permite, sin cargo inicial, a cualquier Usuario:
a) Ejecutar el Software para cualquier proposito.
b) Estudiar y modificar el codigo fuente.
c) Distribuir copias literales o modificadas, siempre que se mantenga este mismo Statuto
   y se cumplan las condiciones de retribucion del Articulo 4.

**Restriccion a Oligarcas:** Ningun Oligarca Tecnologico puede usar el Software bajo
este regimen de acceso libre. DEBE adquirir una Bula (Articulo 14) o acogerse al
regimen de retribucion del Articulo 4.

**Nota sobre licencias OSI/FSF:** Este Statuto NO busca aprobacion OSI. Es una
licencia de **commons compensado**, distinta del open source tradicional porque
reconoce que el trabajo humano detras del codigo tiene derecho a retribucion.
Open Source significa "codigo abierto", no "codigo gratuito para oligopolios".

### 3. Regimen de Propiedad Privada (Bulas y Excepciones)

**3.1 Principio General**
El Software bajo este Statuto es, por defecto, abierto. La propiedad privada del codigo
(cierre de fuente) SOLO es posible mediante la adquisicion de una **Bula** (Articulo 14).

**3.2 Salario, no Limosna**
Si un Usuario comercial necesita modificaciones, mejoras o integracion del Software:
- **Opcion A (Salario)**: Contratar al Desarrollador original o a un mantenedor
  certificado a precio de mercado por el trabajo especifico, MAS el % de usufructo
  legitimo acordado entre las partes.
- **Opcion B (Proyecto)**: Pagar por el desarrollo de la mejora como proyecto
  independiente, con precio de gestor de proyecto + % de usufructo.
- **Opcion C (Bula)**: Adquirir una Bula que cubre 7 anos de propiedad privada
  y derecho a modificar sin publicar fuentes (Articulo 14).

**3.3 Auto-Favorito en GitHub (Diezmo Digital Minimo para Usuarios Gratuitos)**
Todo Usuario que se beneficie del Software sin retribucion economica reconoce la
deuda moral de otorgar el *star* en GitHub como gesto minimo de gratitud.
Si el Proyecto esta en GitHub{f" ({self.github_repo})" if self.github_repo else ""},
el Usuario se compromete a marcarlo como favorito. Cuesta cero dolares y salda la
deuda de reconocimiento. Compartir, forkear o mencionar el proyecto tambien son
actos validos de restitucion moral.

**3.4 Acceso Libre y Gratuito (Umbral de Pobreza Energetica)**
El Software es de uso irrestricto, gratuito y perpetuo SIN DERECHO A SOPORTE para:
- Individuos y estudiantes.
- Desarrolladores independientes cuyo poder adquisitivo sea inferior al umbral de
  pobreza: **salario minimo del G20 multiplicado por 3**, medido en **Big Macs**
  (BME) o en **Kilowatts-hora (kWE)** como metrica de densidad energetica.
  En {country_code.upper()}, esto equivale a ~{t["poor_dev_usd"]:,.0f} USD/mes.
- Proyectos de codigo abierto bajo cualquier licencia aprobada por OSI o FSF,
  siempre que el proyecto no cobre por el uso del Software en si.
- Instituciones educativas y organizaciones sin animo de lucro con presupuesto inferior
  a ${t["nonprofit_max"]:,.0f} USD anuales.
- Cooperativas y proyectos de infraestructura publica.
- Empresas de economia fisica cuyos ingresos brutos anuales no superen
  ${t["ingresos_brutos_alto"]:,.0f} USD.

### 4. Deber de Retribucion ("Diezmo Tecnologico")

La tasa de retribucion se determina segun el Ingreso Disponible Mensual del Usuario
expresado en BME (Big Mac Equivalents). El Usuario debe autoevaluar su categoria y
aplicar la tasa correspondiente sobre el **Margen Bruto Operativo** (Articulo 1).

**Escala Impositiva Universal (1% a 10%) sobre el Margen Bruto Operativo:**

**4.0 Diezmo Comercial sin Compliance (0.5% - 3%) — VM, SaaS y Backend**
Cuando el Software se ejecuta en maquinas virtuales 100% privadas, como backend SaaS,
o en infraestructura operativa no publica, el Usuario comercial NO requiere contrato
de compliance pero DEBE pagar el Diezmo Comercial simplificado, auto-declarado:

| Facturacion Anual (USD) | Diezmo | Tasa al Fondo |
|------------------------|--------|---------------|
| < $1M | 0.5% del Margen Bruto Operativo | 5% del diezmo |
| $1M - $10M | 1% del Margen Bruto Operativo | 5% del diezmo |
| $10M - $100M | 2% del Margen Bruto Operativo | 5% del diezmo |
| > $100M | 3% del Margen Bruto Operativo | 5% del diezmo |

**El diezmo sin compliance es auto-declarado.** El Usuario calcula su Margen Bruto
Operativo anual y transfiere el porcentaje correspondiente al proyecto via GitHub
Sponsors o a la Fundacion RNS (Articulo 15). Si la Fundacion RNS detecta mediante
el crawler (Articulo 5) que el Usuario declaro un monto inferior al real, se aplica
el recargo por Derivative Work (Articulo 5.4) y el caso escala a mediacion (Articulo 16).

Este diezmo sin compliance es la **via pragmatica** para empresas que no necesitan
soporte ni auditoria, pero que SI usan el Software comercialmente. Es mas barato
que el diezmo con compliance, pero si se detecta evasion, la multa es
significativamente mayor.

**4.1 Escala Impositiva con Compliance (1% a 10%)**

{brackets_text}

**4.2 Base de Calculo: Margen Bruto Operativo**
El diezmo se calcula sobre el Margen Bruto Operativo, NO sobre los ingresos brutos.
Se permite deducir:
- Costos de hardware existente (servidores, almacenamiento, ancho de banda).
- Costos de personal humano directamente vinculado al Software.
- Costos de licencias de terceros necesarias.

NO se permite deducir inversiones en escalabilidad (nuevos servidores, expansion),
costos de adquisicion de usuarios, ni gastos financieros. **Esto evita la estrategia
Jeff Bezos**: declarar perdidas operativas mediante inversion masiva mientras se
extrae valor real del trabajo ajeno.

**4.3 — Tabla Plana Corporativa (Alternativa Simplificada)**
Ademas del sistema BME, el Usuario puede optar por la **Tabla Plana Corporativa**,
que ofrece precios fijos segun facturacion anual. Se aplica el menor de los dos:

| Facturacion Anual (USD) | Precio Anual | Tasa al Fondo |
|------------------------|-------------|---------------|
| < $100K | $0 (Open Source gratuito) | $0 |
| $100K - $1M | $500/ano | $25 (5%) |
| $1M - $10M | $2,500/ano | $125 (5%) |
| $10M - $100M | $10,000/ano | $500 (5%) |
| $100M - $1B | $50,000/ano | $2,500 (5%) |
| > $1B (Oligarca) | 0.1% de facturacion (min $100K) | 5% del precio |

El **5% de cada pago** se destina automaticamente al **Fondo de Sostenibilidad**
para financiar mantenedores de infraestructura critica y repositorios huerfanos.

**4.4 Metricas por Tipo de Negocio**

| Tipo de Negocio | Metrica de Calculo | Prorrateo |
|----------------|-------------------|-----------|
| **SaaS** | % del Margen Bruto Operativo del servicio | Si RNS es el 10% del codigo pero es critico (Articulo 1.1), se paga el 100% del diezmo. Si es accesorio, se prorratea por acuerdo. |
| **Middleware/API** | Por **trafico**: $ por llamada o GB transferido | Se mide por volumen de peticiones que pasan por el componente RNS. |
| **Desktop App** | % del ingreso bruto por venta de licencias | Todo producto bajo RNS compite por el 20% del margen. |
| **Embedded (hardware)** | Por **unidad vendida**: precio fijo por dispositivo | Igual para un dispositivo de $10 que uno de $10,000. El costo es por unidad, no por valor. |
| **Marketplace** | Paga **quien usa las librerias RNS** directamente | El marketplace no paga por sus vendedores; cada vendedor que integre RNS paga su diezmo. |
| **Publicidad/Freeware** | % del ingreso por publicidad atribuible al Software | Se prorratea segun el porcentaje de usuarios que interactuan con el componente RNS. |

**4.5 Pago en codigo o en licencia**
Para empresas con Margen Bruto Operativo anual inferior a
${t["ingresos_brutos_alto"]:,.0f} USD, el Usuario podra optar por:
- Contribuir codigo aprobado al proyecto original (al menos 5% del esfuerzo total de
  desarrollo), o
- Abonar el porcentaje correspondiente segun su BME.

**4.6 Tramo corporativo**
Para empresas con Margen Bruto Operativo anual igual o superior a
${t["ingresos_brutos_alto"]:,.0f} USD, el Usuario abonara el porcentaje de su tramo BME,
con un minimo del 5%.

**4.7 Modelo Deuda para Startups (0% Interes Real)**
Las startups con facturacion anual inferior a $500,000 USD y menos de 3 anos de
operacion pueden acogerse al **Modelo Deuda**:
- Adquieren una **Licencia-Deuda** que difiere el pago del diezmo.
- **Interes**: 0% real. Para el **Sur Global**, el interes es **0% directo en moneda
  local**. Para el **Norte Global**, el interes es solo la inflacion del periodo.
- El pago se activa cuando la startup supera los $500,000 USD de facturacion anual
  o a los 5 anos, lo que ocurra primero.
- La deuda se garantiza con un porcentaje de participacion futura o con un aval.

**4.8 Modelo WinRAR para PYMEs**
Las PYMEs establecidas podran utilizar el Software sin pago inicial durante los
primeros 18 meses. Transcurrido ese periodo, si la PYME ha superado los
${t["ingresos_brutos_pyme"]:,.0f} USD de ingresos anuales vinculados, debera:
- Adquirir una Bula (Articulo 14), o
- Acogerse al plan de credito al desarrollo (Articulo 4.5), o
- Negociar un acuerdo de pagos atrasados bajo el modelo WinRAR (Articulo 7).

### 5. Auditoria, Cumplimiento y Sistema de Recompensas

**5.1 Mecanismo de Auditoria**
El cumplimiento de este Statuto se verifica mediante:
- **Autodeclaracion**: Todo Usuario comercial debe presentar una declaracion jurada
  anual de uso del Software, Margen Bruto Operativo y diezmo pagado.
- **Auditoria Comunitaria**: Cualquier mantenedor o contribuyente activo puede
  solicitar una declaracion jurada a un Usuario sospechoso de incumplimiento.
- **Crawler de Codigo Abierto**: La Fundacion RNS (Articulo 15) mantiene un bot
  de escaneo publico que detecta uso de codigo RNS en repositorios publicos y
  privados (via fingerprinting) y cruza con los registros de pago.

**5.2 Sistema de Recompensas (Delator parte de la multa)**
Si un tercero (persona fisica o moral) detecta y reporta un caso de uso no declarado
del Software por parte de un Oligarca Tecnologico o corporacion:
- El delator recibe el **30% de la multa** resultante.
- El delator permanece anonimo si asi lo solicita.
- La denuncia se presenta ante la Fundacion RNS, que inicia el proceso de mediacion
  (Articulo 16).

**5.3 Multas y Sanciones**
Si se determina incumplimiento:
- **Multa**: 2x el diezmo no pagado + intereses (tasa de inflacion del pais del
  infractor + 2%).
- **Oligarca Reincidente**: Si un Oligarca Tecnologico es hallado culpable de
  incumplimiento, se le impone una **licencia forzosa de 20 anos**: debe adquirir
  una Bula (Articulo 14) por 20 anos (no 7) al precio de Oligarca + 50% de recargo.
  Los fondos adicionales se destinan integramente a los mantenedores del proyecto
  afectado.

**5.4 Derivative Work sin Fork — Montaje de Software (Clausula Anti-Ensamblaje)**
Quien modifica, extiende o construye una obra derivada del Software sin haber
realizado un **fork publico** en GitHub o GitLab y sin haber notificado al
Autor, comete **Montaje de Software sin Acuerdo de Fork**. Esto constituye:
- Violacion del Articulo 8 (Excomunion Digital).
- Violacion del Septimo Mandamiento (Exodo 20:15): *No robaras*.
- Apropiacion indebida de trabajo ajeno.

**Sancion por Montaje sin Fork:**
- **Recargo del 50%** sobre el Diezmo correspondiente (sea sin compliance Art. 4.0
  o con compliance Art. 4.1) desde la fecha del primer uso detectado.
- **Inhabilitacion** para adquirir Bulas (Art. 14) por un periodo de 7 anos
  desde la deteccion.
- **Registro publico** del infractor en la lista negra de la Fundacion RNS
  (Art. 15), visible en el crawler publico.

**Exencion:** Si el Derivative Work se realiza mediante un fork publico en GitHub
o GitLab con atribucion clara al Autor original y notificacion al repositorio
original via issue/PR, no hay sancion. El fork es el **acto de buena fe** que
demuestra intencion de compliance.

### 6. Clausula Anti-Parasitaria

Toda entidad cuyo modelo de negocio principal sea la especulacion fiduciaria o la
extraccion de rentas sobre deuda NO posee licencia gratuita. Si una corporacion de
Big Tech, fondo de cobertura, aseguradora, o entidad financiera integra este trabajo
en un servicio comercial, el uso de este material constituye una deuda de Restitucion
Material del 10% fijo sobre el Margen Bruto Operativo.

**Rerum Novarum es pro-trabajo humano.** Las entidades que reemplazan trabajadores
humanos por automatizacion basada en este Software sin retribuir a los desarrolladores
originales incurren en parasitismo economico y violacion del Septimo Mandamiento
(Exodo 20:15).

### 7. Retroactividad (Modelo WinRAR)

**7.1 Principio General**
Este Statuto reconoce que la justicia no prescribe. Sin embargo, para ser juridicamente
ejecutable, el modelo de retroactividad sigue el **Metodo WinRAR**:
- Si un Usuario es descubierto usando el Software sin haber pagado el diezmo, se le
  presenta una **negociacion asistida**: pagar los diezmos atrasados con un recargo
  del 10% + intereses (inflacion local + 2%), o enfrentar la demanda.
- Si el Usuario acepta la negociacion y paga, se regulariza su situacion y puede
  continuar usando el Software bajo el Statuto.
- Si el Usuario rechaza la negociacion, la Fundacion RNS (Articulo 15) inicia el
  proceso de mediacion (Articulo 16).

**7.2 Deuda desde el Primer Uso**
La deuda se calcula desde el primer ciclo de procesamiento en que se ejecuto el
Software con fines de lucro. Sin embargo, la obligacion de pago solo es exigible
judicialmente desde la fecha de publicacion de este Statuto (v4.0) en adelante.
Los periodos anteriores se consideran **deuda moral** sujeta a negociacion, no a
accion judicial, siguiendo el principio de seguridad juridica.

**7.3 Cese de Uso = No Deuda Adicional**
Si un Usuario cesa completamente el uso del Software, no se genera deuda adicional
a partir del cese. La deuda acumulada hasta el cese sigue siendo exigible.

### 8. Excomunion Digital

La violacion de los terminos de este Statuto resultara en la "Excomunion Digital":
- Denegacion de licencias futuras.
- Orden de purga del codigo de los servidores de la entidad infractora.
- Publicacion del incumplimiento en el registro publico de la Fundacion RNS.
- Bloqueo de ejecucion en red: los mantenedores pueden distribuir listas negras
  de IPs/dominios que usen el Software sin licencia.
- Lo que la corporacion se niega a pagar, el codigo se niega a compilar.

### 9. Compatibilidad

Este Statuto no es compatible con GPL, MIT, Apache ni Creative Commons estandar
en tanto no se respete el capitulo de retribucion. Cualquier obra derivada debe
mantenerse bajo este mismo Statuto. Sin embargo, el conocimiento y las skills
derivadas del Software se rigen por el principio GNU: el conocimiento es libre;
lo que se licencia aqui es la implementacion material, no la idea.

**RNS es una licencia de commons compensado**, no una licencia open source
tradicional. No busca aprobacion OSI porque el open source clasico no resuelve
el problema de los mantenedores miserables y las empresas que valen mas que
naciones enteras.

### 10. No-Remuneracion = No-Soporte (Clausula del Cumplimiento)

**10.1 Ausencia de Garantia por Defecto**
EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTIA DE NINGUN TIPO, EXPRESA O IMPLICITA,
INCLUYENDO PERO NO LIMITADO A GARANTIAS DE COMERCIALIZACION, IDONEIDAD PARA UN PROPOSITO
PARTICULAR Y NO INFRACCION. EL DESARROLLADOR NO SERA RESPONSABLE DE DANOS DIRECTOS O
INDIRECTOS.

**10.2 Soporte Solo para Contribuyentes**
El Derecho a soporte tecnico, respuesta a issues, parches de seguridad prioritarios y
actualizaciones de compatibilidad SOLO se concede a:
- Usuarios que hayan adquirido una **Bula** (Articulo 14).
- Usuarios que paguen el **Diezmo Tecnologico** (Articulo 4) al Fondo de Sostenibilidad.
- Mantenedores activos que contribuyan codigo al proyecto.

**10.3 El Usuario Gratuito no puede exigir Soporte**
Quien usa el Software sin retribuir no tiene derecho a exigir:
- Correccion de bugs en un plazo determinado.
- Implementacion de features solicitadas.
- Respuesta a issues o pull requests.
- Compatibilidad con versiones futuras.

Esto no es crueldad: es justicia. **Si no pagas salario, no tienes empleado.
Si no contribuyes, no eres cliente. Eres un beneficiario del bien comun,
y el bien comun no tiene servicio al cliente.**

### 11. Del Jubileo del Codigo (Clausula del Septimo Ano)

**11.1 Ciclo del Jubileo**
Cada 7 anos desde la ultima version major publicada, el Software entra en un periodo
de *Jubileo Tecnologico*. Durante este periodo:
- El codigo fuente completo se congela como **version STD** (Standard).
- La STD se convierte en la version canonica mantenida por la comunidad bajo los
  terminos de este Statuto.
- El Autor o entidad mantenedora podra continuar desarrollando versiones privativas
  paralelas previa adquisicion de una nueva Bula, pero la STD queda bajo gobernanza
  comunitaria (Articulo 13).

**11.2 El Jubileo y las Bulas**
Cuando expira una Bula (7 anos desde su emision), el codigo asociado a ella entra
automaticamente en Jubileo y se libera como STD. No se puede adquirir una segunda
Bula sobre el mismo codigo. Esto evita el **Caso Disney** (Mickey Mouse): la
extension perpetua de derechos de autor mediante renovacion infinita.

**11.3 Proposito del Jubileo**
El Jubileo persigue:
- **Competitividad**: Estandarizar el codigo para que terceros puedan construir
  sobre una base solida, reduciendo la dependencia de un solo proveedor.
- **Preservacion**: Evitar que el conocimiento tecnologico quede atrapado en
  versiones cerradas u olvidadas.
- **Relevo generacional**: Permitir que nuevas generaciones de desarrolladores
  tomen el relevo cuando el ciclo natural del proyecto lo requiera.

**11.4 Proximo Jubileo**
El proximo Jubileo de este proyecto ocurre en {next_jubilee_year}.

### 12. De la Liberacion por Abandono (Clausula del Cuidado Pastoral)

**12.1 Causas de Liberacion**
El Software bajo este Statuto sera automaticamente liberado como STD si ocurre
CUALQUIERA de las siguientes condiciones:
- **a) Abandono de Soporte**: El soporte al publico inicial cae por debajo del
  50% de los usuarios registrados o estimados en la primera version estable.
- **b) Obsolescencia Tecnologica**: El software permanece sin releases de
  cualquier tipo (major, minor o patch) por un periodo de 2 anos o mas.
- **c) Silencio del Autor**: El Autor o entidad mantenedora no responde a
  comunicaciones oficiales durante 6 meses consecutivos.

**12.2 Efectos de la Liberacion**
Al activarse la Liberacion por Abandono:
- Todo el codigo fuente, incluyendo ramas privadas vinculadas contractualmente
  al proyecto pero cubiertas por Bula expirada, pasa a ser **STD automatica**.
- La comunidad puede bifurcar (fork) el proyecto y continuar su desarrollo bajo
  el nombre original, siempre que mantenga el presente Statuto.
- Cualquier entidad que haya derivado valor comercial del Software durante el
  periodo de abandono debera compensar retroactivamente al Fondo de Sostenibilidad.

**12.3 Notificacion y Plazos**
Antes de la liberacion, se intentara notificar al Autor por:
- Correo electronico registrado (3 intentos, 30 dias entre cada uno).
- Publicacion en el repositorio oficial del proyecto (issue pinned por 90 dias).
- Aviso en el registro publico de la Fundacion RNS (Articulo 15).

### 13. De la Gobernanza STD (Clausula del Consenso Comunitario)

**13.1 Creacion de una STD**
Una version STD se declara por consenso de la comunidad de contribuyentes activos.
Se requiere:
- **Acuerdo del 60%** de los contribuyentes que hayan realizado al menos una
  contribucion en los ultimos 12 meses.
- Votacion en el repositorio oficial, con periodo de discusion minimo de 30 dias.
- El resultado se documenta en `STD-MANIFEST.md` en la raiz del proyecto.

**13.2 Poderes de la Comunidad STD**
La comunidad que mantiene una STD tiene autoridad para:
- Aprobar cambios *breaking* que mejoren la seguridad, interoperabilidad o rendimiento.
- Bifurcar el proyecto oficial si el Autor se opone sistematicamente al bien comun.
- Elegir un comite de mantenedores STD por periodos de 2 anos.
- Transferir la STD a otra organizacion si el repositorio original desaparece.

**13.3 Limites de la Gobernanza STD**
La comunidad STD NO puede:
- Cambiar el Statuto a uno mas restrictivo.
- Eliminar las clausulas de compensacion economica.
- Apropiarse del nombre o marca sin consentimiento del Autor.
- Cobrar por el acceso al codigo fuente.

### 14. De las Bulas (Propiedad Privada Temporal)

**14.1 Naturaleza de la Bula**
La Bula es un titulo de propiedad privada temporal sobre el Software. Quien adquiere
una Bula puede:
- Mantener el codigo fuente cerrado (no publicarlo) por un maximo de 7 anos.
- Desarrollar versiones privativas derivadas sin obligacion de publicar fuentes.
- Exigir soporte tecnico del Autor original segun los terminos acordados.
- Recibir parches de seguridad prioritarios durante la vigencia de la Bula.

**14.2 Limite Absoluto: Una Bula por Proyecto**
Solo se puede adquirir **UNA Bula por proyecto en toda su historia**.
Cuando la Bula expira (7 anos), el codigo se libera como STD bajo Jubileo.
No es posible renovar la Bula ni adquirir una segunda. Esto es asi para evitar
el **Caso Disney**: la extension perpetua de derechos de autor que congelo
la cultura y el conocimiento durante decadas.

**14.3 Precio de la Bula: % de Ingresos Anuales de la Division**
El precio de la Bula se calcula como un **porcentaje de los ingresos anuales de la
division o linea de negocio** que utiliza el Software:
- **Desarrollador independiente** (BME < 500): ${t["poor_dev_usd"] * 3:.0f} USD
  (equivalente a 3 meses de ingreso disponible local).
- **PYME** (BME 500-5000): 2% de los ingresos anuales de la division × 7.
- **Corporacion** (BME > 5000): 5% de los ingresos anuales de la division × 7.
- **Oligarca Tecnologico**: 10% de los ingresos anuales de la division × 7,
  con un minimo de ${t["ingresos_brutos_alto"] * 0.50:.0f} USD × 7 =
  ${t["ingresos_brutos_alto"] * 0.50 * 7:.0f} USD.

**14.4 Destino de los Fondos de Bulas**
El 100% de los ingresos por Bulas se destina al **Fondo de Sostenibilidad**,
que paga salarios de:
- Mantenedores de infraestructura critica (Tailwind, Linux Foundation, kernel,
  compiladores, gestores de paquetes, etc.)
- Correctores de seguridad y auditores de codigo.
- Traductores y documentadores de proyectos esenciales.
- Infraestructura de computo para CI/CD y distribucion.

**14.5 Bula no es Perpetuidad**
La Bula no transfiere la propiedad intelectual del proyecto. El Autor original
conserva la titularidad de los derechos. La Bula es un derecho de uso privativo
temporal, no una compra del proyecto. Las Bulas no son transferibles ni heredables.
Al expirar, el codigo vuelve al acervo comun.

### 15. Gobernanza del Statuto (Fundacion Rerum Novarum)

**15.1 Creacion de la Fundacion**
Se crea la **Fundacion Rerum Novarum** (FRN), una organizacion sin animo de lucro
con sede en el **Sur Global** (America Latina, Africa o Asia), constituida como
fundacion hermana de la **Free Software Foundation** (FSF) pero especializada en
licencias de commons compensado.

**15.2 Composicion del Comite de Gobierno**
El gobierno de la FRN se organiza siguiendo los principios de la **Politeia
Aristotelico-Tomista**: gobierno de los mas virtuosos y capaces, no de los mas
ricos. El comite se compone de:
- **Miembros electos**: 5 mantenedores elegidos por voto ponderado por meritos
  (contribuciones, antiguedad, impacto de proyectos mantenidos).
- **Miembros por interes**: 3 representantes de la comunidad de usuarios
  (PYMEs, instituciones educativas, cooperativas).
- **Miembros fundadores**: 2 miembros designados por los creadores originales
  del Statuto.

**15.3 Votacion por Meritos (Politeia Aristotelicotomista)**
El sistema de votacion emula el sistema electoral de Estados Unidos pero aplicado
al merito tecnologico:
- Cada contribuyente activo recibe **votos segun sus meritos**: 1 voto base + 1
  voto adicional por cada ano de contribucion activa + 1 voto adicional por cada
  proyecto mantenido con mas de 1,000 usuarios.
- Los mantenedores de infraestructura critica (definida en Articulo 1) reciben
  un multiplicador de 2x en su peso de voto.
- Las decisiones requieren:
  - Mayoría simple (50%+1) para cambios operativos.
  - Mayoría calificada (60%) para cambios al Statuto.
  - Unanimidad (100%) para eliminar los articulos irrenunciables (Art. 17.4).

**15.4 Metodo de Gestion: SCRUM**
La gestion de la FRN sigue la metodologia **SCRUM**:
- **Sprints** de 3 meses para la distribucion del Fondo de Sostenibilidad.
- **Sprint Planning** al inicio de cada trimestre para priorizar pagos.
- **Sprint Review** al final con transparencia publica de gastos.
- **Retrospectiva** anual para mejorar el proceso.

**15.5 Distribucion del Fondo de Sostenibilidad**
Los recursos del Fondo se distribuyen asi:
- 60% a mantenedores de infraestructura critica (pagos recurrentes).
- 20% a proyectos de seguridad y auditoria.
- 10% a traduccion y documentacion.
- 10% a infraestructura tecnica (servidores, CI/CD, distribucion).

### 16. Mediacion y Resolucion de Disputas

**16.1 Proceso de 3 Pasos**
Toda disputa bajo este Statuto se resuelve mediante el siguiente proceso,
en orden obligatorio:

**Paso 1 — Mediacion Comunitaria (30 dias)**
- Cualquier disputa entre partes se presenta ante la Fundacion RNS.
- La FRN designa un mediador comunitario de una lista de mantenedores certificados.
- El mediador tiene 30 dias para facilitar un acuerdo entre las partes.
- Si se alcanza un acuerdo, se firma un acta de mediacion vinculante.

**Paso 2 — Arbitraje (60 dias)**
- Si la mediacion falla, la disputa pasa a arbitraje vinculante.
- El arbitraje se realiza ante la **Camara de Comercio Internacional (ICC)**
  o una camara de arbitraje del Sur Global designada por la FRN.
- El arbitro tiene 60 dias para emitir un laudo.
- El laudo es vinculante para ambas partes.

**Paso 3 — Tribunales Nacionales (ultimo recurso)**
- Si alguna de las partes no cumple el laudo arbitral, la parte cumplidora puede
  recurrir a los tribunales nacionales competentes.
- La FRN provee asistencia legal a los mantenedores individuales.

**16.2 Ley Aplicable**
Este Statuto se rige por los principios del Derecho Natural y la equidad
internacional. En caso de conflicto de leyes, se aplica la ley del domicilio
del Desarrollador original del Software.

### 17. Disposiciones Finales

- Si algun tribunal considerase inaplicable alguna clausula, se sustituira por la maxima
  retribucion permitida por la ley, preservando el espiritu de la *Rerum Novarum*.
- El Desarrollador se compromete a destinar al menos el 20% de las regalias recibidas
  al Fondo de Sostenibilidad para sostener a otros desarrolladores bajo este Statuto.
- Este Statuto reconoce que la tecnologia debe servir al Bien Comun y a la prosperidad
  material de las naciones, prohibiendo su secuestro por entidades de especulacion
  financiera y monopolios nominalistas.
- Los Articulos 11 (Jubileo), 12 (Liberacion por Abandono), 13 (Gobernanza STD),
  14 (Bulas) y 15 (Fundacion RNS) son **irrenunciables**: ninguna modificacion de
  este Statuto puede eliminarlos o reducirlos.
- **Mantenedores de infraestructura critica** (ej: Tailwind, Linux Foundation,
  proyectos con >10M descargas/mes) tienen prioridad en la asignacion del Fondo de
  Sostenibilidad.
- Las disputas se resuelven segun el proceso del Articulo 16.
- Este Statuto se inspira en las fuentes de la **Doctrina Social de la Iglesia**
  (Rerum Novarum, Quadragesimo Anno, Centesimus Annus, Laborem Exercens) y el
  **Decalogo** (Exodo 20:1-17), pero no requiere adhesion religiosa para su uso.
  Es un instrumento juridico basado en la Ley Natural, accesible a toda persona
  de buena voluntad independientemente de su credo.

---

*Statuto generado el {datetime.now().strftime("%Y-%m-%d")} para {country_code.upper()}.
Redactado bajo el espiritu de la Meta Dialectica Escolastica (MDE), la Escuela de
Salamanca, y la Doctrina Social de la Iglesia, en la ciudad virtual de Salamanca,
por el Magister Determinans del Concilio.*

[![License: Rerum Novarum Statuto 5.0](https://img.shields.io/badge/License-Rerum_Novarum_5.0-purple.svg)](LICENSE.md)

---
**Registro RNS:** Para registrar tu proyecto bajo este Statuto, generar una Bula,
o realizar un pago, visita:
  concilio license --register --name "Tu Proyecto" --repo "https://github.com/..."
  concilio license --pay --project "tu-proyecto" --amount 2500
  concilio license --bula --holder "Tu Empresa" --project "tu-proyecto"

El 5% de cada pago se destina al Fondo de Sostenibilidad para mantener
infraestructura critica y rescatar repositorios huerfanos.
"""

    def save_license(self, path: str, country_code: str = "US"):
        content = self.generate_license(country_code)
        Path(path).write_text(content, encoding="utf-8")
        return path

    @classmethod
    def list_countries(cls):
        return sorted(BIG_MAC_INDEX.keys())

    @staticmethod
    def flat_price(annual_revenue: float) -> dict:
        """Calcula el precio segun la tabla plana corporativa.

        Args:
            annual_revenue: Facturacion anual de la empresa en USD.

        Returns:
            dict con 'price_usd', 'tier', 'tier_name', 'orphan_contribution'
        """
        for lo, hi, price, name in FLAT_PRICE_TABLE:
            if lo <= annual_revenue < hi:
                if isinstance(price, float) and price < 1:
                    price = max(annual_revenue * price, 100_000)
                return {
                    "price_usd": price,
                    "tier": name,
                    "tier_name": name,
                    "orphan_contribution": round(price * ORPHAN_FUND_RATE, 2),
                }
        return {"price_usd": 0, "tier": "Gratis", "tier_name": "Gratis", "orphan_contribution": 0}

    @classmethod
    def calculate_bme(
        cls,
        monthly_income_usd: float,
        residence_country: str,
        income_country: Optional[str] = None,
    ) -> dict:
        bme = BigMacCalculator.disposable_income_bme(
            monthly_income_usd, residence_country, income_country
        )
        rate, label, _ = BigMacCalculator.get_tax_bracket(bme)
        return {
            "bme": round(bme, 1),
            "tasa": f"{rate * 100:.0f}%",
            "categoria": label,
            "big_mac_precio": BigMacCalculator.big_mac_price(residence_country),
        }
