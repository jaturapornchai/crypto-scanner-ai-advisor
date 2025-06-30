package main

import (
	"testing"
	"time"
	utils "tread2/pkg"
)

func TestStringHelper_Capitalize(t *testing.T) {
	sh := utils.NewStringHelper()

	tests := []struct {
		input    string
		expected string
	}{
		{"hello", "Hello"},
		{"WORLD", "World"},
		{"", ""},
		{"a", "A"},
		{"tEST", "Test"},
	}

	for _, test := range tests {
		result := sh.Capitalize(test.input)
		if result != test.expected {
			t.Errorf("Capitalize(%q) = %q; expected %q", test.input, result, test.expected)
		}
	}
}

func TestStringHelper_Reverse(t *testing.T) {
	sh := utils.NewStringHelper()

	tests := []struct {
		input    string
		expected string
	}{
		{"hello", "olleh"},
		{"12345", "54321"},
		{"a", "a"},
		{"", ""},
		{"Go", "oG"},
	}

	for _, test := range tests {
		result := sh.Reverse(test.input)
		if result != test.expected {
			t.Errorf("Reverse(%q) = %q; expected %q", test.input, result, test.expected)
		}
	}
}

func TestStringHelper_IsPalindrome(t *testing.T) {
	sh := utils.NewStringHelper()

	tests := []struct {
		input    string
		expected bool
	}{
		{"racecar", true},
		{"hello", false},
		{"A man a plan a canal Panama", true},
		{"race a car", false},
		{"", true},
		{"a", true},
	}

	for _, test := range tests {
		result := sh.IsPalindrome(test.input)
		if result != test.expected {
			t.Errorf("IsPalindrome(%q) = %v; expected %v", test.input, result, test.expected)
		}
	}
}

func TestTimeHelper_IsWeekend(t *testing.T) {
	th := utils.NewTimeHelper()

	// Saturday
	saturday := time.Date(2023, 12, 2, 12, 0, 0, 0, time.UTC)
	if !th.IsWeekend(saturday) {
		t.Error("Expected Saturday to be weekend")
	}

	// Sunday
	sunday := time.Date(2023, 12, 3, 12, 0, 0, 0, time.UTC)
	if !th.IsWeekend(sunday) {
		t.Error("Expected Sunday to be weekend")
	}

	// Monday (weekday)
	monday := time.Date(2023, 12, 4, 12, 0, 0, 0, time.UTC)
	if th.IsWeekend(monday) {
		t.Error("Expected Monday to not be weekend")
	}
}

func TestMathHelper_Divide(t *testing.T) {
	mh := utils.NewMathHelper()

	tests := []struct {
		a, b     float64
		expected float64
		hasError bool
	}{
		{10, 2, 5, false},
		{15, 3, 5, false},
		{10, 0, 0, true},
		{0, 5, 0, false},
	}

	for _, test := range tests {
		result, err := mh.Divide(test.a, test.b)

		if test.hasError {
			if err == nil {
				t.Errorf("Divide(%.2f, %.2f) expected error but got none", test.a, test.b)
			}
		} else {
			if err != nil {
				t.Errorf("Divide(%.2f, %.2f) unexpected error: %v", test.a, test.b, err)
			}
			if result != test.expected {
				t.Errorf("Divide(%.2f, %.2f) = %.2f; expected %.2f", test.a, test.b, result, test.expected)
			}
		}
	}
}
