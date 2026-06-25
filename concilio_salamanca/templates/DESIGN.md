# DESIGN.md — Brand Contract

> Este archivo define el contrato visual del proyecto.
> Todo codigo frontend generado por el Concilio debe respetar estas directrices.
> Usado por Magister Delineationis y Open-Design para generar prototipos consistentes.

## 1. Paleta de Colores

```yaml
colors:
  primary: "#000000"        # Color principal de marca
  secondary: "#FFFFFF"      # Color secundario
  accent: "#3366FF"         # Color de acento (CTAs, links)
  neutral:
    100: "#F5F5F5"
    200: "#E5E5E5"
    500: "#888888"
    900: "#111111"
  success: "#00CC66"
  warning: "#FFAA00"
  error: "#FF3344"
  background:
    light: "#FFFFFF"
    dark: "#0A0A0A"
  text:
    light: "#111111"
    dark: "#F5F5F5"
```

## 2. Tipografía

```yaml
typography:
  font_family:
    primary: "Inter, -apple-system, sans-serif"
    mono: "JetBrains Mono, SF Mono, monospace"
  sizes:
    h1: "2rem"
    h2: "1.5rem"
    h3: "1.25rem"
    body: "1rem"
    small: "0.875rem"
    caption: "0.75rem"
  weights:
    regular: 400
    medium: 500
    semibold: 600
    bold: 700
```

## 3. Espaciado (Grid Base 8px)

```yaml
spacing:
  unit: 8                   # Grid base en px
  xs: 4                     # 4px
  sm: 8                     # 8px
  md: 16                    # 16px
  lg: 24                    # 24px
  xl: 32                    # 32px
  xxl: 64                   # 64px
  section: 128              # 128px
```

## 4. Bordes y Sombras

```yaml
border:
  radius:
    sm: 4px
    md: 8px
    lg: 16px
    full: 9999px
  width: 1px
shadow:
  sm: "0 1px 3px rgba(0,0,0,0.1)"
  md: "0 4px 12px rgba(0,0,0,0.15)"
  lg: "0 8px 24px rgba(0,0,0,0.2)"
```

## 5. Animación

```yaml
animation:
  duration:
    fast: 150ms
    normal: 300ms
    slow: 500ms
  easing:
    default: "cubic-bezier(0.4, 0, 0.2, 1)"
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)"
    linear: "linear"
  transitions: ["opacity", "transform", "background-color", "color", "box-shadow"]
```

## 6. Breakpoints (Responsive)

```yaml
breakpoints:
  mobile: 640px
  tablet: 1024px
  desktop: 1280px
  wide: 1536px
```

## 7. Modo Oscuro / Claro

```yaml
dark_mode:
  supported: true            # false si solo hay modo claro
  strategy: "prefers-color-scheme"  # CSS media query
  auto: true                 # Seguir preferencia del sistema
```

## 8. Voz del Producto

```yaml
voice:
  tone: "professional"      # professional | casual | playful | technical
  vocabulary:
    - usa "tu" no "usted"
    - evita jerga tecnica innecesaria
    - mensajes de error en lenguaje humano
  anti_patterns:
    - "hemos detectado un error" → "Algo salio mal"
    - "sesion expirada" → "Tu sesion termino. Inicia sesion de nuevo."
```

## 9. Accesibilidad (WCAG)

```yaml
accessibility:
  level: "AA"               # AA minimo, AAA preferible
  contrast_ratio: 4.5       # Texto normal: 4.5:1, texto grande: 3:1
  focus_visible: true       # Outline visible en foco
  aria_labels: true         # Todos los elementos interactivos con aria-label
  reduced_motion: true      # Respetar prefers-reduced-motion
```
