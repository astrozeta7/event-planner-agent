import re
from typing import Dict, Any, Optional, List
from datetime import datetime


class ConversationalAgent:
    
    def __init__(self):
        self.conversation_state = {}
    
    async def process_message(
        self, 
        message: str, 
        current_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        message_lower = message.lower()
        
        extracted_data = self._extract_information(message, current_data)
        
        missing_fields = self._get_missing_required_fields(extracted_data)
        
        ready_to_search = len(missing_fields) == 0
        
        response_message = self._generate_response(
            message_lower, 
            extracted_data, 
            missing_fields,
            ready_to_search
        )
        
        return {
            "message": response_message,
            "updated_data": extracted_data,
            "ready_to_search": ready_to_search,
            "missing_fields": missing_fields
        }
    
    def _extract_information(
        self, 
        message: str, 
        current_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        data = current_data.copy()
        message_lower = message.lower()
        
        if not data.get('event_date'):
            date = self._extract_date(message)
            if date:
                data['event_date'] = date
        
        if not data.get('location'):
            location = self._extract_location(message)
            if location:
                data['location'] = location
        
        if not data.get('number_of_guests'):
            guests = self._extract_number_of_guests(message)
            if guests:
                data['number_of_guests'] = guests
        
        if not data.get('budget_per_guest'):
            budget = self._extract_budget(message)
            if budget:
                data['budget_per_guest'] = budget
        
        if not data.get('cuisine_preferences') or len(data.get('cuisine_preferences', [])) == 0:
            cuisines = self._extract_cuisines(message)
            if cuisines:
                data['cuisine_preferences'] = cuisines
        
        if not data.get('event_type'):
            event_type = self._extract_event_type(message)
            if event_type:
                data['event_type'] = event_type
        
        needs_room = self._extract_needs_room(message_lower)
        if needs_room is not None:
            data['needs_event_room'] = needs_room
        
        if not data.get('special_requirements'):
            special_req = self._extract_special_requirements(message)
            if special_req:
                data['special_requirements'] = special_req
        
        return data
    
    def _extract_date(self, message: str) -> Optional[str]:
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',
            r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message.lower())
            if match:
                try:
                    date_str = match.group(0)
                    if '-' in date_str and len(date_str) == 10:
                        return date_str
                    elif '/' in date_str:
                        parts = date_str.split('/')
                        return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                except:
                    pass
        
        return None
    
    def _extract_location(self, message: str) -> Optional[str]:
        location_keywords = ['in', 'at', 'near', 'around']
        cities = [
            'san francisco', 'new york', 'los angeles', 'chicago', 'houston',
            'phoenix', 'philadelphia', 'san antonio', 'san diego', 'dallas',
            'austin', 'seattle', 'boston', 'miami', 'atlanta', 'denver',
            'portland', 'las vegas', 'detroit', 'nashville'
        ]
        
        message_lower = message.lower()
        
        for city in cities:
            if city in message_lower:
                return city.title()
        
        for keyword in location_keywords:
            pattern = f'{keyword}\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)'
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_number_of_guests(self, message: str) -> Optional[int]:
        patterns = [
            r'(\d+)\s*(?:guests?|people|persons?|attendees?)',
            r'(?:for|about|around|approximately)\s*(\d+)',
            r'(\d+)\s*(?:person|people)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        return None
    
    def _extract_budget(self, message: str) -> Optional[float]:
        patterns = [
            r'\$(\d+(?:\.\d{2})?)\s*(?:per\s*(?:guest|person|head))',
            r'budget.*?\$(\d+(?:\.\d{2})?)',
            r'(\d+)\s*dollars?\s*(?:per\s*(?:guest|person))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        
        return None
    
    def _extract_cuisines(self, message: str) -> Optional[List[str]]:
        cuisines = [
            'italian', 'chinese', 'japanese', 'mexican', 'indian', 'thai',
            'french', 'mediterranean', 'american', 'greek', 'spanish',
            'korean', 'vietnamese', 'middle eastern', 'brazilian'
        ]
        
        found_cuisines = []
        message_lower = message.lower()
        
        for cuisine in cuisines:
            if cuisine in message_lower:
                found_cuisines.append(cuisine.title())
        
        return found_cuisines if found_cuisines else None
    
    def _extract_event_type(self, message: str) -> Optional[str]:
        event_types = {
            'wedding': ['wedding', 'marriage', 'nuptial'],
            'corporate': ['corporate', 'business', 'company', 'conference'],
            'birthday': ['birthday', 'bday', 'birth day'],
            'anniversary': ['anniversary'],
            'graduation': ['graduation', 'grad party'],
            'baby shower': ['baby shower'],
            'holiday': ['holiday', 'christmas', 'thanksgiving'],
            'fundraiser': ['fundraiser', 'charity', 'gala']
        }
        
        message_lower = message.lower()
        
        for event_type, keywords in event_types.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return event_type
        
        return None
    
    def _extract_needs_room(self, message_lower: str) -> Optional[bool]:
        yes_keywords = ['need venue', 'need room', 'need space', 'venue', 'event room', 'event space']
        no_keywords = ['no venue', 'no room', 'no space', 'have venue', 'have room']
        
        for keyword in no_keywords:
            if keyword in message_lower:
                return False
        
        for keyword in yes_keywords:
            if keyword in message_lower:
                return True
        
        return None
    
    def _extract_special_requirements(self, message: str) -> Optional[str]:
        dietary_keywords = [
            'vegetarian', 'vegan', 'gluten-free', 'nut-free', 'dairy-free',
            'kosher', 'halal', 'allergy', 'allergies', 'dietary'
        ]
        
        message_lower = message.lower()
        
        for keyword in dietary_keywords:
            if keyword in message_lower:
                return message
        
        return None
    
    def _get_missing_required_fields(self, data: Dict[str, Any]) -> List[str]:
        required_fields = {
            'event_date': 'event date',
            'location': 'location',
            'number_of_guests': 'number of guests'
        }
        
        missing = []
        for field, label in required_fields.items():
            if not data.get(field):
                missing.append(label)
        
        return missing
    
    def _generate_response(
        self, 
        message_lower: str, 
        extracted_data: Dict[str, Any],
        missing_fields: List[str],
        ready_to_search: bool
    ) -> str:
        if ready_to_search:
            return (
                f"Perfect! I have all the information I need:\n\n"
                f"📅 Date: {extracted_data['event_date']}\n"
                f"📍 Location: {extracted_data['location']}\n"
                f"👥 Guests: {extracted_data['number_of_guests']}\n"
                f"{f'🍽️ Cuisine: {', '.join(extracted_data.get('cuisine_preferences', []))}' if extracted_data.get('cuisine_preferences') else ''}\n"
                f"{f'💰 Budget: ${extracted_data['budget_per_guest']}/guest' if extracted_data.get('budget_per_guest') else ''}\n\n"
                f"Let me search for the best options for you!"
            )
        
        if len(missing_fields) > 0:
            if len(missing_fields) == 3:
                return (
                    "Great! Let me help you plan your event. "
                    "To get started, I need a few key details:\n\n"
                    "1️⃣ When is your event? (e.g., 2025-09-15)\n"
                    "2️⃣ Where will it be? (e.g., San Francisco)\n"
                    "3️⃣ How many guests are you expecting?"
                )
            else:
                return (
                    f"Thanks! I still need to know:\n\n"
                    f"{chr(10).join([f'• {field.title()}' for field in missing_fields])}\n\n"
                    f"Could you provide these details?"
                )
        
        return "Got it! Is there anything else you'd like to add or change?"
