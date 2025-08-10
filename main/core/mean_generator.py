import random

class MeanTimeGeneratorMS:
    def __init__(self, target_ms=5000, range_pct=20, precision_ms=1):
        self.target_ms = target_ms
        self.range_pct = range_pct
        self.precision_ms = precision_ms
        self.reset()

    def reset(self, target_ms=None, range_pct=None, precision_ms=None):
        """Reset state and optionally reconfigure generator."""
        if target_ms is not None:
            self.target_ms = target_ms
        if range_pct is not None:
            self.range_pct = range_pct
        if precision_ms is not None:
            self.precision_ms = precision_ms

        self.range_ms = (self.range_pct / 100) * self.target_ms
        self.total = 0
        self.count = 0
        self.last_value = None
        self.last_mean = None
        self.last_error_ms = None
        self.last_error_pct = None

    def next_value(self):
        """Generate the next value and update stats."""
        self.count += 1
        current_mean = self.total / self.count if self.count > 1 else self.target_ms

        # Random base value within range
        value = random.uniform(self.target_ms - self.range_ms,
                               self.target_ms + self.range_ms)

        # Soft adjustment toward target
        adjustment = (self.target_ms - current_mean) * 0.3
        value += adjustment

        # Clamp to range
        value = max(self.target_ms - self.range_ms,
                    min(self.target_ms + self.range_ms, value))

        # Round to desired precision
        value = round(value / self.precision_ms) * self.precision_ms

        self.total += value
        accumulated_mean = self.total / self.count
        error_ms = accumulated_mean - self.target_ms
        error_pct = (error_ms / self.target_ms) * 100 if self.target_ms else None

        # Save last stats
        self.last_value = value
        self.last_mean = accumulated_mean
        self.last_error_ms = error_ms
        self.last_error_pct = error_pct

        return value #, accumulated_mean, self.target_ms, error_ms, error_pct

    # Extra getters
    def get_count(self):
        return self.count

    def get_last_value(self):
        return self.last_value

    def get_last_mean(self):
        return self.last_mean

    def get_last_error_ms(self):
        return self.last_error_ms

    def get_last_error_pct(self):
        return self.last_error_pct

    def get_stats(self):
        """Return all current stats in a dict."""
        return {
            "count": self.count,
            "last_value": self.last_value,
            "last_mean": self.last_mean,
            "target": self.target_ms,
            "last_error_ms": self.last_error_ms,
            "last_error_pct": self.last_error_pct
        }

    def __iter__(self):
        """Allow use in a for loop."""
        while True:
            yield self.next_value()

import random

class MeanTimeGeneratorSeconds:
    def __init__(self, target_s=5, range_pct=20, precision_s=0.1):
        self.target_s = target_s
        self.range_pct = range_pct
        self.precision_s = precision_s
        self.reset()

    def reset(self, target_s=None, range_pct=None, precision_s=None):
        """Reset state and optionally reconfigure generator."""
        if target_s is not None:
            self.target_s = target_s
        if range_pct is not None:
            self.range_pct = range_pct
        if precision_s is not None:
            self.precision_s = precision_s

        self.range_s = (self.range_pct / 100) * self.target_s
        self.total = 0
        self.count = 0
        self.last_value = None
        self.last_mean = None
        self.last_error_s = None
        self.last_error_pct = None

    def next_value(self):
        """Generate the next value and update stats."""
        self.count += 1
        current_mean = self.total / self.count if self.count > 1 else self.target_s

        # Random base value within range
        value = random.uniform(self.target_s - self.range_s,
                               self.target_s + self.range_s)

        # Soft adjustment toward target
        adjustment = (self.target_s - current_mean) * 0.3
        value += adjustment

        # Clamp to range
        value = max(self.target_s - self.range_s,
                    min(self.target_s + self.range_s, value))

        # Round to desired precision
        value = round(value / self.precision_s) * self.precision_s

        self.total += value
        accumulated_mean = self.total / self.count
        error_s = accumulated_mean - self.target_s
        error_pct = (error_s / self.target_s) * 100 if self.target_s else None

        # Save last stats
        self.last_value = value
        self.last_mean = accumulated_mean
        self.last_error_s = error_s
        self.last_error_pct = error_pct

        return value

    # Extra getters
    def get_count(self):
        return self.count

    def get_last_value(self):
        return self.last_value

    def get_last_mean(self):
        return self.last_mean

    def get_last_error_s(self):
        return self.last_error_s

    def get_last_error_pct(self):
        return self.last_error_pct

    def get_stats(self):
        """Return all current stats in a dict."""
        return {
            "count": self.count,
            "last_value": self.last_value,
            "last_mean": self.last_mean,
            "target": self.target_s,
            "last_error_s": self.last_error_s,
            "last_error_pct": self.last_error_pct
        }

    def __iter__(self):
        """Allow use in a for loop."""
        while True:
            yield self.next_value()



class MeanTimeGeneratorInt:
    def __init__(self, target_s: int = 5, range_pct: int = 50, precision_s: int = 1):
        self.target_s = target_s
        self.range_pct = range_pct
        self.precision_s = precision_s
        self.reset()

    def reset(self, target_s=None, range_pct=None, precision_s=None):
        """Reset state and optionally reconfigure generator."""
        if target_s is not None:
            self.target_s = target_s
        if range_pct is not None:
            self.range_pct = range_pct
        if precision_s is not None:
            self.precision_s = precision_s

        self.range_s = int((self.range_pct / 100) * self.target_s)
        self.total = 0
        self.count = 0
        self.last_value = None
        self.last_mean = None
        self.last_error_s = None
        self.last_error_pct = None

    def next_value(self) -> int:
        """Generate the next integer value and update stats."""
        self.count += 1
        current_mean = self.total / self.count if self.count > 1 else self.target_s

        # Random base value within range (using randint for integers)
        value = random.randint(
            int(self.target_s - self.range_s),
            int(self.target_s + self.range_s)
        )

        # Soft adjustment toward target (rounded to integer)
        adjustment = int(round((self.target_s - current_mean) * 0.3))
        value += adjustment

        # Clamp to range (ensuring integers)
        value = max(
            int(self.target_s - self.range_s),
            min(int(self.target_s + self.range_s), value)
        )

        # Round to desired precision (still returns integer if precision_s is 1)
        value = int(round(value / self.precision_s) * self.precision_s)

        # Update stats
        self.total += value
        accumulated_mean = self.total / self.count
        error_s = accumulated_mean - self.target_s
        error_pct = (error_s / self.target_s) * 100 if self.target_s else None

        # Save last stats
        self.last_value = value
        self.last_mean = accumulated_mean
        self.last_error_s = error_s
        self.last_error_pct = error_pct
        return self.total # value
    

    # Resto de métodos (get_count, get_last_value, etc.) se mantienen igual...
    def get_count(self):
        return self.count

    def get_last_value(self):
        return self.last_value

    def get_last_mean(self):
        return self.last_mean

    def get_last_error_s(self):
        return self.last_error_s

    def get_last_error_pct(self):
        return self.last_error_pct
    
    def get_total_value(self):
        return self.total
    
    def get_stats(self):
        """Return all current stats in a dict."""
        return {
            "count": self.count,
            "total":self.total,
            "last_value": self.last_value,
            "last_mean": self.last_mean,
            "target": self.target_s,
            "last_error_s": self.last_error_s,
            "last_error_pct": self.last_error_pct
        }

    def __iter__(self):
        """Allow use in a for loop."""
        while True:
            yield self.next_value()

# Example usage
if __name__ == "__main__":
    gen = MeanTimeGeneratorMS(target_ms=5000, range_pct=50, precision_ms=100)

    for _ in range(50):
        value = gen.next_value()
        # print(f"Value: {value} ms | Mean: {mean:.2f} ms | Target: {target} ms | "
        #       f"Error: {err_ms:+.2f} ms ({err_pct:+.2f}%)")
        print("value:", value)
    print("Stats:", gen.get_stats())
    
    gen = MeanTimeGeneratorSeconds(target_s=5, range_pct=50, precision_s=0.5)
    for _ in range(10):
        value = gen.next_value()
        print(f"Value: {value} s")

    print("Stats:", gen.get_stats())
