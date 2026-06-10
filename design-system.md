# Design System - Dashboard Admin

Nguồn phân tích: `frontend/src/app/dashboard/admin/page.tsx`, `frontend/tailwind.config.ts`, và component phụ `frontend/src/components/pipeline/PipelineHistorySection.tsx`.

## 1. Tổng Quan Phong Cách Thiết Kế

- **Phong cách giao diện:** dark terminal dashboard, tối giản, kỹ thuật, operational/admin.
- **Cảm giác thị giác:** giống bảng điều khiển nội bộ cho hệ thống pipeline: nền đen, chữ mono, viền mảnh, nhiều badge/chip/status nhỏ.
- **Nguyên tắc nổi bật:**
  - Ưu tiên mật độ thông tin cao.
  - Ít trang trí, không card lớn hoặc hero.
  - Tất cả section chia bằng border, spacing gọn.
  - Trạng thái hệ thống thể hiện bằng màu semantic: xanh, vàng, đỏ.
  - Dùng typography mono + uppercase + tracking rộng để tạo cảm giác terminal/system.

## 2. Màu Sắc

Các màu chính lấy từ `tailwind.config.ts`, không phải ước lượng.

| Vai trò | Token hiện tại | HEX |
|---|---:|---:|
| Nền chính | `terminal.bg` | `#0c0c0c` |
| Nền phụ / surface | `terminal.surface` | `#141414` |
| Border / divider | `terminal.border` | `#2a2a2a` |
| Text chính | `terminal.text` | `#d4d4d4` |
| Text phụ | `terminal.muted` | `#5c5c5c` |
| Primary / accent | `terminal.accent` | `#f0b429` |
| Success | `terminal.green` | `#4ade80` |
| Warning | `terminal.amber` | `#fbbf24` |
| Error | `terminal.red` | `#f87171` |
| Info | Chưa xác định trong terminal theme | Chưa xác định |

Hover/focus/active thường dùng alpha:

- Accent hover bg: `#f0b429` với opacity `5%`, `10%`, `20%`.
- Accent border hover: `#f0b429` với opacity `30%`, `40%`, `50%`, `70%`.
- Row hover: `terminal.border/20` hoặc `terminal.border/30`.
- Disabled: opacity `30%`, `40%`, `50%`.

Lưu ý: `PipelineHistorySection` có dùng `text-terminal-blue` và `text-terminal-purple`, nhưng hai màu này **chưa được define** trong `tailwind.config.ts`.

## 3. Font Chữ Và Typography

### Font family

Trang admin override trực tiếp:

```ts
"'JetBrains Mono', 'Fira Code', 'Consolas', monospace"
```

Brand title dùng:

```ts
font-display = Syne, sans-serif
```

### Kích thước chữ

| Vai trò | Class | Kích thước |
|---|---:|---:|
| Brand title | `text-base` | `16px` |
| Section heading | `text-sm` | `14px` |
| Body / item title | `text-xs` | `12px` |
| Label / metadata | `text-[10px]` | `10px` |
| Badge rất nhỏ | `text-[9px]` | `9px` |
| Icon-only pagination text | `text-[10px]` | `10px` |

### Font weight

- Brand: `font-bold`, uppercase, tracking `0.2em`.
- Section heading: `font-semibold`, uppercase, `tracking-widest`.
- Row title/symbol: `font-semibold` hoặc `font-bold`.
- Badge/button: `font-medium` hoặc `font-semibold`.
- Metadata: regular, muted.

### Line height

- Chủ yếu dùng Tailwind default.
- Nội dung mô tả dài dùng `leading-relaxed`.
- Không thấy định nghĩa line-height riêng toàn cục.

## 4. Spacing

### Container

- Header: `px-6 py-3` -> ngang `24px`, dọc `12px`.
- Main content: `p-6` -> `24px`.

### Grid / section

- Main grid: `grid-cols-12 gap-5` -> gap `20px`.
- Cột trái: `col-span-5`.
- Cột phải: `col-span-7`.
- Section stack: `space-y-5` -> `20px`.

### Section header

- Header section: `gap-3`, `pb-3`, `mb-4`.
- Icon box: `h-8 w-8`.
- Title/subtitle nằm sát nhau, không có margin riêng.

### Component spacing phổ biến

- Row/card item: `px-3 py-2.5`.
- Small button: `px-2 py-1`.
- Large action button: `px-4 py-2`.
- Chips/badges: `px-1.5 py-0.5` hoặc `px-2 py-1`.
- Internal gap nhỏ: `gap-1`, `gap-1.5`, `gap-2`.
- Internal gap trung bình: `gap-3`, `gap-4`.

## 5. Layout

- **Kiểu bố cục:** top navbar + 12-column dashboard grid.
- **Căn lề:** full-width, không có max-width container.
- **Main structure:**
  - Header full width.
  - Content padding `24px`.
  - Grid 12 cột.
  - Cột trái 5/12: News Sources, Tracked Symbols.
  - Cột phải 7/12: Wiki, Pipeline Actions, Run History.
- **Card layout:** không dùng card lớn bọc toàn section; từng row/list item mới là surface card.
- **Responsive behavior:** Chưa có responsive class cho main grid. Suy luận: hiện tại có thể chưa tối ưu mobile vì `col-span-5` và `col-span-7` cố định trên mọi viewport. Một số text trong history có `hidden sm:block`, nhưng layout chính chưa responsive.

## 6. Component Style

### Button

- **Background:** thường transparent hoặc `terminal.accent/5`, `terminal.accent/10`.
- **Text:** `terminal.accent`, `terminal.muted`, hoặc semantic color.
- **Border:** `1px solid terminal.border` hoặc accent/semantic opacity.
- **Radius:** `rounded` -> khoảng `4px`.
- **Padding:** nhỏ `px-2 py-1`, trung bình `px-4 py-2`.
- **Typography:** mono, `10px` hoặc `11px`, uppercase, tracking rộng.
- **Hover:**
  - Accent button: tăng bg từ `/5` lên `/10` hoặc `/20`.
  - Border tăng opacity.
  - Muted button đổi text sang `terminal.text`.
- **Disabled:** opacity `30-50%`, `cursor-not-allowed`.

### Input / Form

- **Background:** `terminal.bg` `#0c0c0c`.
- **Text:** `terminal.text`.
- **Placeholder:** `terminal.muted/40`.
- **Border:** `terminal.border`.
- **Radius:** `rounded` khoảng `4px`.
- **Padding:** `px-2 py-1`, input lớn hơn `px-2.5 py-1.5`.
- **Focus:** `focus:outline-none`, `focus:border-terminal-accent/50`.
- **Text transform:** nhiều input dùng uppercase.

### Card / Panel / Row

- **Background:** `terminal.surface` `#141414`.
- **Border:** `terminal.border` `#2a2a2a`.
- **Radius:** `rounded` khoảng `4px`.
- **Padding row:** `px-3 py-2.5`.
- **Shadow:** gần như không dùng; chỉ dropdown có `shadow-lg`.
- **Hover:** border accent nhẹ hoặc bg border alpha.

### Navbar / Top Bar

- **Background:** `terminal.surface`.
- **Border:** bottom border `terminal.border`.
- **Padding:** `px-6 py-3`.
- **Layout:** flex, justify-between, center.
- **Brand:** Syne, `16px`, bold, uppercase, tracking `0.2em`, accent vàng.
- **Status:** text `10px`, muted, dot xanh pulse.

### Table / List

Không có table HTML; dùng list row dạng card.

- Row height khoảng `48px`.
- Dữ liệu chia bằng flex.
- Metadata nhỏ `9-10px`.
- Expandable row dùng `border-t` và background `terminal.bg`.

### Modal / Dropdown

- Modal: Chưa xác định.
- Dropdown autocomplete:
  - `absolute`, `z-20`.
  - Background `terminal.surface`.
  - Border `terminal.border`.
  - Radius `rounded`.
  - Shadow `shadow-lg`.
  - Item hover `terminal.accent/10` + text accent.

## 7. Border Radius, Shadow, Icon

### Border radius

Theo config:

- `xs`: `2px`
- `sm`: `4px`
- `md`: `6px`
- `lg`: `8px`
- `xl`: `12px`
- `pill`: `9999px`

Trang admin dùng chủ yếu:

- `rounded` -> mặc định Tailwind khoảng `4px`.
- `rounded-full` cho dot/progress.

### Shadow

- Hầu như không dùng shadow.
- Dropdown có `shadow-lg`.
- Config có `focus-ring`: `0 0 0 2px rgba(59, 130, 246, 0.5)`, nhưng trang này không dùng trực tiếp.

### Icon

- Library: `lucide-react`.
- Style: outline/line icon.
- Kích thước phổ biến:
  - Section icon: `16px` (`h-4 w-4`).
  - Button icon: `12px` (`h-3 w-3`).
  - Action button icon: `14px` (`h-3.5 w-3.5`).
  - Empty state icon: `24px` (`h-6 w-6`).
- Màu:
  - Primary icon: `terminal.accent`.
  - Muted icon: `terminal.muted`.
  - Status icon: green/amber/red.

## 8. Design Tokens Đề Xuất

```css
:root {
  --color-bg: #0c0c0c;
  --color-surface: #141414;
  --color-surface-muted: #2a2a2a;

  --color-primary: #f0b429;
  --color-primary-hover: rgba(240, 180, 41, 0.1);
  --color-primary-border: rgba(240, 180, 41, 0.4);

  --color-text: #d4d4d4;
  --color-text-muted: #5c5c5c;
  --color-border: #2a2a2a;

  --color-success: #4ade80;
  --color-warning: #fbbf24;
  --color-error: #f87171;
  --color-info: #3b82f6; /* Chưa dùng rõ trong admin page */

  --font-sans: "JetBrains Mono", "Fira Code", "Consolas", monospace;
  --font-display: "Syne", sans-serif;

  --text-xs: 9px;
  --text-sm: 10px;
  --text-base: 12px;
  --text-lg: 14px;
  --text-xl: 16px;

  --space-xs: 4px;
  --space-sm: 6px;
  --space-md: 8px;
  --space-lg: 12px;
  --space-xl: 20px;
  --space-2xl: 24px;

  --radius-sm: 2px;
  --radius-md: 4px;
  --radius-lg: 8px;
  --radius-pill: 9999px;

  --shadow-sm: none;
  --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.35);
}
```

## Checklist Áp Dụng Cho Trang Mới

- Dùng nền chính `#0c0c0c`, surface `#141414`, border `#2a2a2a`.
- Dùng font mono cho toàn bộ dashboard; chỉ brand/title lớn mới dùng display font.
- Heading section: `14px`, uppercase, tracking rộng, font-semibold.
- Body item: `12px`; metadata, label, badge: `9-10px`.
- Layout nên theo dashboard grid, spacing chính `20px`, padding page `24px`.
- Không bọc toàn section trong card lớn; dùng border-bottom cho header section và row cards cho từng item.
- Button/input/card đều bo góc nhỏ khoảng `4px`, border mảnh, không shadow.
- Hover chỉ thay đổi nhẹ border/background bằng accent alpha.
- Trạng thái dùng semantic color: success xanh, warning vàng, error đỏ.
- Icon dùng lucide outline, kích thước `12-16px`, màu muted/accent/semantic.
- Nếu làm responsive, cần bổ sung breakpoint cho grid chính vì trang mẫu hiện chưa thể hiện rõ responsive behavior.
