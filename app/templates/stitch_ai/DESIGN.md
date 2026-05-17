---
name: 智汇简历助手
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#444651'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#757682'
  outline-variant: '#c5c5d3'
  surface-tint: '#4059aa'
  primary: '#00236f'
  on-primary: '#ffffff'
  primary-container: '#1e3a8a'
  on-primary-container: '#90a8ff'
  inverse-primary: '#b6c4ff'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#37007e'
  on-tertiary: '#ffffff'
  tertiary-container: '#5200b5'
  on-tertiary-container: '#bc9bff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b6c4ff'
  on-primary-fixed: '#00164e'
  on-primary-fixed-variant: '#264191'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#eaddff'
  tertiary-fixed-dim: '#d2bbff'
  on-tertiary-fixed: '#25005a'
  on-tertiary-fixed-variant: '#5a00c6'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-lg:
    fontFamily: Noto Sans SC
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-lg-mobile:
    fontFamily: Noto Sans SC
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Noto Sans SC
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Noto Sans SC
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Noto Sans SC
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: Noto Sans SC
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1'
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1200px
  gutter: 24px
  margin-desktop: 40px
  margin-mobile: 16px
---

## Brand & Style
The design system is engineered to evoke a sense of **authority, efficiency, and intelligence**. The target audience includes modern professionals and graduates entering a competitive job market where precision and clarity are paramount. 

The aesthetic follows a **Corporate Modern** style with a heavy emphasis on **Minimalism**. By prioritizing generous whitespace and a restricted color palette, the UI directs all focus toward the user's content—their career history. Subtle AI-driven elements are introduced through soft gradients and kinetic transitions to signify the "smart" layer of the product without compromising the professional integrity required for recruitment tools.

## Colors
The palette is anchored by **"Trustworthy Deep Blue"** (#1E3A8A), used for primary actions, navigation, and headers to establish a foundation of reliability. 

**Teal** (#0D9488) serves as the primary accent for AI-enhanced features, such as "Smart Optimize" buttons or suggestions. **Soft Purple** (#7C3AED) is utilized sparingly for high-value AI insights and premium tier indicators. 

Backgrounds are kept strictly in the **White to Light Gray** spectrum to maintain a "document-first" feel, ensuring that resume previews remain the visual priority.

## Typography
This design system utilizes **Noto Sans SC** as the primary typeface to ensure exceptional legibility across Simplified Chinese characters. It provides a neutral, modern tone that balances corporate professionalism with digital approachability.

For alphanumeric data, such as dates, percentages in skill charts, and technical labels, **Inter** is used for its superior geometric clarity. 

Line heights are intentionally set wider (1.6) for body text to reduce cognitive load during long reading sessions of resume drafts.

## Layout & Spacing
The layout follows a **12-column fluid grid** for the main application shell, while resume editing views utilize a **fixed-width centered canvas** to mimic physical paper (A4 ratio).

We employ an 8px spacing scale. Large sections are separated by 48px or 64px to create a sense of breathing room. In the AI "Smart Panel," spacing is tightened to 16px to signify a grouping of related tools. 

**Breakpoints:**
- **Mobile (<768px):** Single column, margins reduced to 16px. Sidebars collapse into bottom sheets.
- **Tablet (768px - 1024px):** 2-column layout (Editor + Preview).
- **Desktop (>1024px):** 3-column capability (Navigation + Editor + AI Assistant Panel).

## Elevation & Depth
Hierarchy is established through **Ambient Shadows** and **Tonal Layering**. 

1.  **Level 0 (Base):** Light gray (#F8FAFC) background.
2.  **Level 1 (Cards):** Pure white surfaces with a 1px border (#E2E8F0) and a very soft, diffused shadow (0px 4px 12px rgba(0,0,0,0.03)).
3.  **Level 2 (Popovers/AI Panels):** Increased shadow depth (0px 10px 25px rgba(0,0,0,0.08)) to indicate temporary interaction layers.

AI elements use a "glow" elevation—a subtle secondary color outer glow—rather than a traditional black shadow, making them feel active and "powered on."

## Shapes
The design system uses a **Rounded** (Level 2) shape language. Standard components like input fields and buttons utilize a 0.5rem (8px) radius. 

Large containers and "Smart Cards" utilize a 1rem (16px) radius to soften the professional environment and make the AI feel more user-friendly. Small tags or "skill chips" use a fully rounded pill shape to distinguish them from actionable buttons.

## Components

### Buttons (按钮)
- **Primary:** Solid Deep Blue with white text. High contrast for "Export PDF" or "Save."
- **AI Action:** Gradient background (Teal to Deep Blue) with a subtle "sparkle" icon prefix.
- **Ghost:** Transparent background with 1px gray border for secondary actions like "Add Section."

### Input Fields (输入框)
Clean, minimal borders that turn Deep Blue on focus. Error states use a soft red (#EF4444) with descriptive Chinese helper text below the field.

### Progress Indicators (进度指示)
A sleek, thin horizontal bar for the resume completion percentage. Completed segments use the Teal accent color to provide a rewarding visual feedback loop.

### AI Insight Cards (AI 建议卡片)
Cards featuring a soft teal left-border accent. These contain "Quick Fix" buttons that allow the user to apply AI suggestions with a single click.

### Data Visualization (数据可视化)
Skill gaps are visualized using horizontal bar charts or "radar" maps with low-opacity fills in Teal, allowing users to quickly identify which areas of their resume need more detail or keywords.