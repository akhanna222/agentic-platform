# 🧮 Modern Calculator App

A beautiful, modern calculator built with the Agentic Platform. Features a stunning gradient design with glassmorphism effects and smooth animations.

## ✨ Features

- **Beautiful Design**: Gradient background with glassmorphism effects
- **Fully Functional**: Addition, subtraction, multiplication, division, and modulo
- **Keyboard Support**: Use your keyboard for faster calculations
- **Responsive**: Works perfectly on mobile and desktop
- **Smooth Animations**: Delightful user experience with transitions
- **Error Handling**: Prevents division by zero

## 🚀 How to Use

### Method 1: Open Directly in Browser

Simply open `index.html` in your web browser:

```bash
cd calculator-app
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or just double-click index.html on Windows
```

### Method 2: Use a Local Server (Recommended)

For the best experience, use a local web server:

```bash
cd calculator-app

# Using Python 3
python3 -m http.server 8080

# Using Python 2
python -m SimpleHTTPServer 8080

# Using Node.js (if you have npx)
npx serve
```

Then open: **http://localhost:8080**

## ⌨️ Keyboard Shortcuts

- **Numbers**: 0-9
- **Decimal**: `.` (period)
- **Operations**:
  - `+` Addition
  - `-` Subtraction
  - `*` Multiplication
  - `/` Division
  - `%` Modulo
- **Calculate**: `Enter` or `=`
- **Clear**: `Escape` or `C`
- **Delete**: `Backspace`

## 📁 File Structure

```
calculator-app/
├── index.html      # Main HTML structure
├── styles.css      # Modern styling with animations
├── script.js       # Calculator logic and functionality
└── README.md       # This file
```

## 🎨 Design Features

- **Gradient Background**: Purple to violet gradient
- **Glassmorphism**: Semi-transparent cards with backdrop blur
- **Smooth Transitions**: 200ms animations on all interactions
- **Hover Effects**: Buttons lift and glow on hover
- **Responsive Grid**: 4-column button layout
- **Modern Typography**: Clean, readable font styles

## 🛠️ Technical Details

- **Pure JavaScript**: No frameworks or dependencies
- **Class-based Architecture**: Clean, maintainable code
- **Error Prevention**: Handles edge cases like multiple decimals, division by zero
- **Floating Point Fix**: Rounds results to avoid JavaScript precision errors

## 📱 Browser Support

Works on all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## 🎯 Example Operations

```
Basic: 5 + 3 = 8
Decimal: 10.5 × 2 = 21
Division: 100 ÷ 4 = 25
Modulo: 17 % 5 = 2
Chain: 5 + 3 × 2 = 16 (evaluates left to right)
```

## 🚀 Built With

**Agentic Platform** - The autonomous AI platform that built this app!

---

**THIS is what an actual app looks like** - not just instructions, but real working code you can open and use! 🎉
