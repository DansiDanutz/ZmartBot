/**
 * Quicksort implementation in JavaScript
 * Time Complexity: O(n log n) average case, O(n²) worst case
 * Space Complexity: O(log n) due to recursive calls
 */

function quicksort(arr, low = 0, high = arr.length - 1) {
    if (low < high) {
        const pivotIndex = partition(arr, low, high);
        quicksort(arr, low, pivotIndex - 1);
        quicksort(arr, pivotIndex + 1, high);
    }
    return arr;
}

function partition(arr, low, high) {
    const pivot = arr[high];
    let i = low - 1;

    for (let j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
    }

    [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
    return i + 1;
}

// Alternative functional implementation
function quicksortFunctional(arr) {
    if (arr.length <= 1) {
        return arr;
    }

    const pivot = arr[Math.floor(arr.length / 2)];
    const left = arr.filter(x => x < pivot);
    const middle = arr.filter(x => x === pivot);
    const right = arr.filter(x => x > pivot);

    return [...quicksortFunctional(left), ...middle, ...quicksortFunctional(right)];
}

// Example usage and tests
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { quicksort, quicksortFunctional };
}

// Test cases
const testArrays = [
    [64, 34, 25, 12, 22, 11, 90],
    [5, 2, 8, 1, 9],
    [1],
    [],
    [3, 3, 3, 3],
    [-5, 2, -8, 1, 0]
];

console.log("Quicksort Test Results:");
testArrays.forEach(arr => {
    const original = [...arr];
    const sorted = quicksort([...arr]);
    console.log(`Original: [${original}] → Sorted: [${sorted}]`);
});

console.log("\nFunctional Quicksort Test Results:");
testArrays.forEach(arr => {
    const original = [...arr];
    const sorted = quicksortFunctional(arr);
    console.log(`Original: [${original}] → Sorted: [${sorted}]`);
});