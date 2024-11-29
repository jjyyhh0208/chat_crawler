import json, re
from datetime import datetime, timedelta


class ChatData:
    """채널톡 API 응답 데이터를 파싱하는 클래스"""

    def __init__(self, response_data: dict):
        """
        채널톡 API 응답 데이터를 파싱하여 객체를 초기화합니다.

        Args:
            response_data (dict): 채널톡 API 응답 데이터
        """
        # 기본값 설정
        self.user_chat_id = None
        self.user_id = None
        self.user_name = None
        self.user_email = None
        self.user_mobile_number = None
        self.chat_time = None
        self.user_chat = None
        self.person_type = None
        self.channel_id = None
        self.assignee_id = None
        self.team_id = None
        self.manager_ids = []
        self.reply_count = 0
        self.tags = []
        self.files = []
        self.role = None

        # API 응답 데이터 파싱
        if response_data:
            self._parse_response(response_data)

    def _parse_response(self, data: dict):
        """API 응답 데이터를 파싱하여 객체 속성을 설정합니다."""
        refers = data.get("refers", {})
        user_chat = refers.get("userChat", {})
        user = refers.get("user", {})
        profile = user.get("profile", {})
        entity = data.get("entity", {})

        # 기본 정보 설정
        self.user_chat_id = user_chat.get("id")
        self.user_id = user_chat.get("userId")
        self.assignee_id = user_chat.get("assigneeId")
        self.team_id = user_chat.get("teamId")
        self.manager_ids = user_chat.get("managerIds", [])
        self.reply_count = user_chat.get("replyCount")
        self.tags = user_chat.get("tags", [])

        # 사용자 프로필 정보
        self.user_name = profile.get("name")
        self.user_mobile_number = profile.get("mobileNumber")
        self.user_email = profile.get("email")

        # 채팅 관련 정보
        self.channel_id = entity.get("channelId")
        self.user_chat = entity.get("plainText")
        self.person_type = entity.get("personType")
        self.files = entity.get("files", [])

        # 채팅 시간 파싱
        created_at = entity.get("createdAt")
        if created_at:
            self.chat_time = self.extract_chat_time(created_at)

        # 역할 설정
        self.role = self.determine_role(self.person_type)

    @staticmethod
    def extract_chat_time(time_str: str) -> datetime:
        """채팅 시간 문자열을 datetime 객체로 변환합니다."""
        try:
            return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def determine_role(person_type: str) -> str:
        """person_type에 따라 역할을 결정합니다."""
        if person_type == "manager":
            return "manager"
        # elif person_type == "alf":
        #     return "alf"
        elif person_type == "user":
            return "user"
        return "unknown"  # bot이나 다른 타입은 unknown으로 처리
