# TypeScript Type Check Summary

## Component Props Reference

### PixelUpload
```typescript
interface PixelUploadProps {
  onFilesSelected: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
  maxFiles?: number;
  maxSizeMB?: number;  // ⚠️ Note: in MB, not bytes
}
```

**Common mistakes:**
- ❌ `maxSize={10 * 1024 * 1024}` (wrong prop name)
- ✅ `maxSizeMB={10}` (correct)

### PixelCard
```typescript
interface PixelCardProps {
  children: ReactNode;
  title?: string;
  className?: string;
  hoverable?: boolean;
  onClick?: () => void;
}
```

**Common mistakes:**
- ❌ `icon={<Icon />}` (not supported)
- ✅ `title="Title"` (correct)

### PixelButton
```typescript
interface PixelButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  loading?: boolean;
  icon?: ReactNode;
}
```

## Fixed Type Errors

1. **PixelCard icon prop** - Removed unsupported `icon` prop
2. **PixelUpload maxSize** - Changed `maxSize` to `maxSizeMB`
3. **Empty page.tsx** - Added placeholder for watermark page

## Build Validation

Before committing code that uses UI components, verify:

```bash
# Check prop names match component interfaces
grep -r "PixelUpload" src/app --include="*.tsx"
grep -r "PixelCard" src/app --include="*.tsx"

# Build to catch type errors
npm run build
```

## Quick Reference

| Component | Common Props | Notes |
|-----------|-------------|-------|
| PixelUpload | onFilesSelected, accept, maxSizeMB | Size in MB |
| PixelCard | title, children, className | No icon prop |
| PixelButton | variant, loading, icon | Extends button HTML |
| PixelModal | isOpen, onClose, title | Boolean isOpen |
| PixelSelect | value, onChange, options/children | Dual mode |
| PixelSlider | value, onChange, min, max | Number value |
| PixelProgress | value, max | Progress bar |
| PixelInput | All standard input props | Extends input HTML |
| PixelTextarea | All standard textarea props | Extends textarea HTML |
| PixelCheckbox | All standard checkbox props | Extends input HTML |
