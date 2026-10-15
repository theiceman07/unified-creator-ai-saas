import re


class Validator:
    def validate_word_budget(self, text: str, max_words: int) -> bool:
        words = len(re.findall(r'\w+', text))
        return words <= max_words

    def validate_banned_words(self, text: str, banned_words: list[str]) -> list[str]:
        found = [word for word in banned_words if word.lower() in text.lower()]
        return found

    def check_platform_limits(self, platform: str, text: str) -> bool:
        limits = {
            'x': 280,
            'linkedin': 3000,
            'youtube_shorts': 100
        }
        if platform in limits:
            return len(text) <= limits[platform]
        return True

validator = Validator()
