# 🎨 ZmartBot App Icon Integration Guide

## Your Custom Z Logo Requirements

### Design Specifications:
- **Style**: High-tech circuit board Z logo (provided)
- **Colors**: Gold/bronze metallic with dark circuit patterns
- **Background**: Dark gradient or transparent
- **Format**: PNG with transparency support

### Required Sizes:

#### iOS Icons:
```
icon.png - 1024x1024px (App Store & iOS devices)
```

#### Android Icons:
```
adaptive-icon.png - 1024x1024px (Adaptive icon foreground)
```

#### Additional:
```
splash-icon.png - 1024x1024px (Launch screen)
favicon.png - 48x48px (Web version)
```

## Implementation Steps:

### 1. Create Icon Files from Your Z Logo:
```bash
# Save your Z logo as these files in assets/images/:
- icon.png (1024x1024)
- adaptive-icon.png (1024x1024) 
- splash-icon.png (1024x1024)
- favicon.png (48x48)
```

### 2. Android Adaptive Icon Setup:
```json
// app.json configuration
"android": {
  "adaptiveIcon": {
    "foregroundImage": "./assets/images/adaptive-icon.png",
    "backgroundColor": "#0B0E11"  // Dark background matching app theme
  }
}
```

### 3. Splash Screen Configuration:
```json
"splash": {
  "image": "./assets/images/splash-icon.png",
  "resizeMode": "contain",
  "backgroundColor": "#0B0E11"  // Match your app's dark theme
}
```

## Design Tips for Your Z Logo:

### For App Icon (icon.png):
- Use your full Z logo with circuit board details
- Ensure it's readable at small sizes (57x57px)
- Add subtle drop shadow for depth
- Keep gold/bronze colors vibrant

### For Android Adaptive (adaptive-icon.png):
- Focus on the Z shape itself
- Reduce fine circuit details that won't show at small sizes
- Ensure it works with different mask shapes (circle, square, rounded)
- Leave 20% safe area around edges

### For Splash Screen (splash-icon.png):
- Can be more detailed than app icon
- Center the Z logo prominently
- Use dark background matching app theme
- Consider adding "ZmartBot" text below

## Color Scheme Recommendations:
```css
Primary Gold: #FFD700
Accent Bronze: #CD7F32
Dark Background: #0B0E11
Circuit Blue: #00C896
```

## Testing:
After adding your icons:
1. Clear Metro cache: `npx expo start --clear`
2. Build new APK: `npx eas build --platform android --profile preview`
3. Install and check app icon appears correctly in device launcher
4. Test different Android launcher styles (Samsung, Nova, etc.)

## Pro Tips:
- Keep the design simple enough to be recognizable at 29x29px (smallest iOS size)
- Test on both light and dark wallpapers
- Consider how it looks in folders and notification badges
- Make sure it aligns with your brand identity