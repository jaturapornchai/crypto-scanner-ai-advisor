package utils

import (
	"fmt"
	"strings"
	"time"
)

// StringHelper provides utility functions for string manipulation
type StringHelper struct{}

// NewStringHelper creates a new StringHelper instance
func NewStringHelper() *StringHelper {
	return &StringHelper{}
}

// Capitalize returns the string with first letter capitalized
func (sh *StringHelper) Capitalize(s string) string {
	if len(s) == 0 {
		return s
	}
	return strings.ToUpper(s[:1]) + strings.ToLower(s[1:])
}

// Reverse returns the reversed string
func (sh *StringHelper) Reverse(s string) string {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}

// IsPalindrome checks if a string is a palindrome
func (sh *StringHelper) IsPalindrome(s string) bool {
	cleaned := strings.ToLower(strings.ReplaceAll(s, " ", ""))
	return cleaned == sh.Reverse(cleaned)
}

// TimeHelper provides utility functions for time manipulation
type TimeHelper struct{}

// NewTimeHelper creates a new TimeHelper instance
func NewTimeHelper() *TimeHelper {
	return &TimeHelper{}
}

// FormatDateTime returns formatted date time string
func (th *TimeHelper) FormatDateTime(t time.Time) string {
	return t.Format("2006-01-02 15:04:05")
}

// IsWeekend checks if the given time is weekend
func (th *TimeHelper) IsWeekend(t time.Time) bool {
	weekday := t.Weekday()
	return weekday == time.Saturday || weekday == time.Sunday
}

// MathHelper provides utility functions for mathematical operations
type MathHelper struct{}

// NewMathHelper creates a new MathHelper instance
func NewMathHelper() *MathHelper {
	return &MathHelper{}
}

// Divide performs division with error handling
func (mh *MathHelper) Divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, fmt.Errorf("cannot divide by zero")
	}
	return a / b, nil
}
