"""
语言和地区检测模块
"""
import re
import emoji
import langid
from typing import Optional, Dict, List
import os

# 国家代码映射
COUNTRY_CODES = {
    'USA': 'US', 'United States': 'US', 'America': 'US',
    'UK': 'GB', 'United Kingdom': 'GB', 'Britain': 'GB', 'England': 'GB',
    'Canada': 'CA',
    'Australia': 'AU',
    'India': 'IN',
    'Germany': 'DE', 'Deutschland': 'DE',
    'France': 'FR',
    'Japan': 'JP', '日本': 'JP',
    'Korea': 'KR', 'South Korea': 'KR', '한국': 'KR',
    'China': 'CN', '中国': 'CN',
    'Brazil': 'BR', 'Brasil': 'BR',
    'Mexico': 'MX', 'México': 'MX',
    'Russia': 'RU', 'Россия': 'RU',
    'Spain': 'ES', 'España': 'ES',
    'Italy': 'IT', 'Italia': 'IT',
    'Netherlands': 'NL', 'Holland': 'NL',
    'Sweden': 'SE', 'Sverige': 'SE',
    'Poland': 'PL', 'Polska': 'PL',
    'Turkey': 'TR', 'Türkiye': 'TR',
    'Indonesia': 'ID',
    'Thailand': 'TH', 'ประเทศไทย': 'TH',
    'Vietnam': 'VN', 'Việt Nam': 'VN',
    'Philippines': 'PH',
    'Malaysia': 'MY',
    'Singapore': 'SG',
    'Argentina': 'AR',
    'Colombia': 'CO',
    'Chile': 'CL',
    'Peru': 'PE',
    'Venezuela': 'VE',
    'Egypt': 'EG', 'مصر': 'EG',
    'Saudi Arabia': 'SA', 'السعودية': 'SA',
    'UAE': 'AE', 'United Arab Emirates': 'AE',
    'Israel': 'IL', 'ישראל': 'IL',
    'South Africa': 'ZA',
    'Nigeria': 'NG',
    'Kenya': 'KE',
}

# Flag emoji到国家代码的映射
FLAG_EMOJI_TO_COUNTRY = {
    '🇺🇸': 'US', '🇬🇧': 'GB', '🇨🇦': 'CA', '🇦🇺': 'AU',
    '🇮🇳': 'IN', '🇩🇪': 'DE', '🇫🇷': 'FR', '🇯🇵': 'JP',
    '🇰🇷': 'KR', '🇨🇳': 'CN', '🇧🇷': 'BR', '🇲🇽': 'MX',
    '🇷🇺': 'RU', '🇪🇸': 'ES', '🇮🇹': 'IT', '🇳🇱': 'NL',
    '🇸🇪': 'SE', '🇵🇱': 'PL', '🇹🇷': 'TR', '🇮🇩': 'ID',
    '🇹🇭': 'TH', '🇻🇳': 'VN', '🇵🇭': 'PH', '🇲🇾': 'MY',
    '🇸🇬': 'SG', '🇦🇷': 'AR', '🇨🇴': 'CO', '🇨🇱': 'CL',
    '🇵🇪': 'PE', '🇻🇪': 'VE', '🇪🇬': 'EG', '🇸🇦': 'SA',
    '🇦🇪': 'AE', '🇮🇱': 'IL', '🇿🇦': 'ZA', '🇳🇬': 'NG',
    '🇰🇪': 'KE'
}

# 域名后缀到国家代码的映射
DOMAIN_TO_COUNTRY = {
    '.us': 'US', '.uk': 'GB', '.ca': 'CA', '.au': 'AU',
    '.in': 'IN', '.de': 'DE', '.fr': 'FR', '.jp': 'JP',
    '.kr': 'KR', '.cn': 'CN', '.br': 'BR', '.mx': 'MX',
    '.ru': 'RU', '.es': 'ES', '.it': 'IT', '.nl': 'NL',
    '.se': 'SE', '.pl': 'PL', '.tr': 'TR', '.id': 'ID',
    '.th': 'TH', '.vn': 'VN', '.ph': 'PH', '.my': 'MY',
    '.sg': 'SG', '.ar': 'AR', '.co': 'CO', '.cl': 'CL',
    '.pe': 'PE', '.ve': 'VE', '.eg': 'EG', '.sa': 'SA',
    '.ae': 'AE', '.il': 'IL', '.za': 'ZA', '.ng': 'NG',
    '.ke': 'KE'
}

# 语言代码到国家的映射（用于推断）
LANGUAGE_TO_COUNTRIES = {
    'en': ['US', 'GB', 'CA', 'AU', 'IN', 'ZA', 'NG', 'KE', 'PH', 'SG'],
    'es': ['ES', 'MX', 'AR', 'CO', 'CL', 'PE', 'VE'],
    'pt': ['BR', 'PT'],
    'fr': ['FR', 'CA', 'BE', 'CH'],
    'de': ['DE', 'AT', 'CH'],
    'it': ['IT'],
    'nl': ['NL', 'BE'],
    'ru': ['RU'],
    'ja': ['JP'],
    'ko': ['KR'],
    'zh': ['CN', 'TW', 'HK', 'SG'],
    'ar': ['SA', 'AE', 'EG', 'MA', 'DZ'],
    'hi': ['IN'],
    'id': ['ID'],
    'th': ['TH'],
    'vi': ['VN'],
    'ms': ['MY'],
    'tr': ['TR'],
    'pl': ['PL'],
    'sv': ['SE'],
    'he': ['IL']
}

class LanguageDetector:
    """语言和地区检测器"""
    
    def __init__(self):
        # 初始化langid
        langid.set_languages(['en', 'es', 'pt', 'fr', 'de', 'it', 'nl', 'ru', 
                              'ja', 'ko', 'zh', 'ar', 'hi', 'id', 'th', 'vi', 
                              'ms', 'tr', 'pl', 'sv', 'he'])
        
        self.no_emoji = os.getenv('KOL_NO_EMOJI', '0') == '1'
    
    def detect_language(self, text: str) -> Optional[str]:
        """检测文本语言"""
        if not text:
            return None
        
        try:
            # 清理文本
            clean_text = self._clean_text_for_detection(text)
            
            # 使用langid检测
            lang, confidence = langid.classify(clean_text)
            
            # 置信度阈值
            if confidence > 0.5:
                return lang
            
            return None
            
        except Exception as e:
            print(f"Language detection error: {e}")
            return None
    
    def extract_country_from_text(self, text: str) -> Optional[str]:
        """从文本中提取国家信息"""
        if not text:
            return None
        
        # 1. 检查Flag emoji
        country = self._extract_country_from_emoji(text)
        if country:
            return country
        
        # 2. 检查文本中的国家名称
        country = self._extract_country_from_names(text)
        if country:
            return country
        
        # 3. 检查域名
        country = self._extract_country_from_domains(text)
        if country:
            return country
        
        # 4. 基于语言推断（作为最后手段）
        lang = self.detect_language(text)
        if lang and lang in LANGUAGE_TO_COUNTRIES:
            # 返回该语言最常见的国家
            return LANGUAGE_TO_COUNTRIES[lang][0]
        
        return None
    
    def _clean_text_for_detection(self, text: str) -> str:
        """清理文本用于语言检测"""
        # 移除URL
        text = re.sub(r'https?://\S+', '', text)
        
        # 移除邮箱
        text = re.sub(r'\S+@\S+', '', text)
        
        # 移除hashtag
        text = re.sub(r'#\w+', '', text)
        
        # 移除@提及
        text = re.sub(r'@\w+', '', text)
        
        # 移除多余空格
        text = ' '.join(text.split())
        
        return text
    
    def _extract_country_from_emoji(self, text: str) -> Optional[str]:
        """从emoji中提取国家"""
        if self.no_emoji:
            return None
        
        emojis = emoji.emoji_list(text)
        for emoji_dict in emojis:
            emoji_char = emoji_dict['emoji']
            if emoji_char in FLAG_EMOJI_TO_COUNTRY:
                return FLAG_EMOJI_TO_COUNTRY[emoji_char]
        
        return None
    
    def _extract_country_from_names(self, text: str) -> Optional[str]:
        """从国家名称中提取"""
        text_lower = text.lower()
        
        for country_name, code in COUNTRY_CODES.items():
            if country_name.lower() in text_lower:
                return code
        
        return None
    
    def _extract_country_from_domains(self, text: str) -> Optional[str]:
        """从域名中提取国家"""
        # 查找所有URL
        urls = re.findall(r'https?://[^\s]+', text)
        
        for url in urls:
            for domain_suffix, country in DOMAIN_TO_COUNTRY.items():
                if domain_suffix in url:
                    return country
        
        return None
    
    def format_country_display(self, country_code: str) -> str:
        """格式化国家显示（处理emoji降级）"""
        if not country_code:
            return ''
        
        if self.no_emoji:
            # ASCII降级
            return f"[{country_code}]"
        else:
            # 尝试显示flag emoji
            # 转换国家代码到flag emoji
            if len(country_code) == 2:
                # 转换为区域指示符
                flag = ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in country_code.upper())
                return flag
            
            return f"[{country_code}]"


def extract_country_from_text(text: str) -> Optional[str]:
    """便捷函数：从文本中提取国家"""
    detector = LanguageDetector()
    return detector.extract_country_from_text(text)


def detect_language(text: str) -> Optional[str]:
    """便捷函数：检测语言"""
    detector = LanguageDetector()
    return detector.detect_language(text)
