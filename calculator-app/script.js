/**
 * Modern Calculator Logic
 * Supports basic arithmetic operations with a beautiful UI
 */

class Calculator {
    constructor() {
        this.currentValue = '0';
        this.previousValue = '';
        this.operation = null;
        this.shouldResetDisplay = false;
        this.history = '';

        this.displayElement = document.getElementById('display');
        this.historyElement = document.getElementById('history');
    }

    /**
     * Append a number or decimal point to the current value
     */
    appendNumber(number) {
        // If we just calculated, start fresh
        if (this.shouldResetDisplay) {
            this.currentValue = '';
            this.shouldResetDisplay = false;
        }

        // Prevent multiple decimal points
        if (number === '.' && this.currentValue.includes('.')) {
            return;
        }

        // Replace initial zero unless adding decimal
        if (this.currentValue === '0' && number !== '.') {
            this.currentValue = number;
        } else {
            this.currentValue += number;
        }

        this.updateDisplay();
    }

    /**
     * Set the operation to perform
     */
    operation(op) {
        // If we already have an operation, calculate first
        if (this.operation !== null && !this.shouldResetDisplay) {
            this.calculate();
        }

        this.operation = op;
        this.previousValue = this.currentValue;
        this.shouldResetDisplay = true;

        // Update history display
        this.history = `${this.previousValue} ${op}`;
        this.updateHistory();
    }

    /**
     * Perform the calculation
     */
    calculate() {
        if (this.operation === null || this.previousValue === '') {
            return;
        }

        const prev = parseFloat(this.previousValue);
        const current = parseFloat(this.currentValue);

        if (isNaN(prev) || isNaN(current)) {
            return;
        }

        let result = 0;

        switch (this.operation) {
            case '+':
                result = prev + current;
                break;
            case '-':
                result = prev - current;
                break;
            case '×':
                result = prev * current;
                break;
            case '÷':
                if (current === 0) {
                    this.displayElement.textContent = 'Error';
                    this.animateCalculation();
                    setTimeout(() => {
                        this.clear();
                    }, 1500);
                    return;
                }
                result = prev / current;
                break;
            case '%':
                result = prev % current;
                break;
            default:
                return;
        }

        // Round to avoid floating point errors
        result = Math.round(result * 100000000) / 100000000;

        // Update history
        this.history = `${this.previousValue} ${this.operation} ${this.currentValue} =`;
        this.updateHistory();

        // Update display
        this.currentValue = result.toString();
        this.operation = null;
        this.previousValue = '';
        this.shouldResetDisplay = true;

        this.animateCalculation();
        this.updateDisplay();
    }

    /**
     * Clear all values
     */
    clear() {
        this.currentValue = '0';
        this.previousValue = '';
        this.operation = null;
        this.shouldResetDisplay = false;
        this.history = '';
        this.updateDisplay();
        this.updateHistory();
    }

    /**
     * Delete last character
     */
    delete() {
        if (this.shouldResetDisplay) {
            return;
        }

        this.currentValue = this.currentValue.slice(0, -1);

        if (this.currentValue === '' || this.currentValue === '-') {
            this.currentValue = '0';
        }

        this.updateDisplay();
    }

    /**
     * Update the main display
     */
    updateDisplay() {
        this.displayElement.textContent = this.currentValue;
    }

    /**
     * Update the history display
     */
    updateHistory() {
        this.historyElement.textContent = this.history;
    }

    /**
     * Add animation effect when calculating
     */
    animateCalculation() {
        this.displayElement.classList.add('calculating');
        setTimeout(() => {
            this.displayElement.classList.remove('calculating');
        }, 500);
    }
}

// Initialize calculator when page loads
const calculator = new Calculator();

// Add keyboard support
document.addEventListener('keydown', (e) => {
    // Numbers
    if (e.key >= '0' && e.key <= '9') {
        calculator.appendNumber(e.key);
    }

    // Decimal point
    if (e.key === '.') {
        calculator.appendNumber('.');
    }

    // Operations
    if (e.key === '+') calculator.operation('+');
    if (e.key === '-') calculator.operation('-');
    if (e.key === '*') calculator.operation('×');
    if (e.key === '/') {
        e.preventDefault(); // Prevent browser search
        calculator.operation('÷');
    }
    if (e.key === '%') calculator.operation('%');

    // Calculate
    if (e.key === 'Enter' || e.key === '=') {
        e.preventDefault();
        calculator.calculate();
    }

    // Clear
    if (e.key === 'Escape' || e.key.toLowerCase() === 'c') {
        calculator.clear();
    }

    // Delete
    if (e.key === 'Backspace') {
        e.preventDefault();
        calculator.delete();
    }
});

console.log('🧮 Calculator initialized!');
console.log('💡 Tip: You can use your keyboard too!');
