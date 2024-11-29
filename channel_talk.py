import json, re, requests, base64
from time import sleep
from datetime import datetime, timedelta


class ChannelTalk:
    """채널톡 API 연결 클래스"""

    def __init__(
        self,
        user_chat_id: str,  # ChatData 객체 대신 직접 chat_id를 받음
        x_access_key: str,
        x_access_secret: str,
        group_id=None,
        bot_name=None,
    ):
        if not x_access_key or not x_access_secret:
            raise ValueError("Access Key and Access Secret must be set")

        self.user_chat_id = user_chat_id
        self.x_access_key = x_access_key
        self.x_access_secret = x_access_secret
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "x-access-key": self.x_access_key,
            "x-access-secret": self.x_access_secret,
        }
        self.base_url = "https://api.channel.io"
        self.group_id = group_id
        self.bot_name = bot_name

    def get_user_chat_messages(self, order="asc", limit=25):
        """
        유저 채팅 메시지를 가져옵니다. 기본적으로 오래된 데이터를 먼저 가져옵니다.
        모든 데이터를 가져오기 위해 페이징 처리 추가.
        """
        print("get_user_chat_messages 실행")

        api_url = f"{self.base_url}/open/v5/user-chats/{self.user_chat_id}/messages"
        all_messages = []  # 모든 메시지를 저장할 리스트
        params = {"sort": order, "limit": limit}

        while True:
            try:
                response = self._send_request_get_json("get", api_url, params=params)

                messages = response.get("messages", [])
                if not messages:
                    break

                all_messages.extend(messages)

                next_cursor = response.get("next")
                if not next_cursor:
                    break

                params["since"] = next_cursor

            except Exception as e:
                print(f"오류 발생: {str(e)}")
                break

        # 모든 메시지를 수집한 후 한 번에 처리
        processed_messages = []
        for message in all_messages:
            if message.get("personType") in ["manager", "user"]:
                sender = message.get("personType")

                if message.get("files"):
                    processed_messages.append(
                        {"sender": sender, "message": "[사진 전송]"}
                    )

                for block in message.get("blocks", []):
                    if block.get("type") == "text":
                        processed_messages.append(
                            {"sender": sender, "message": block.get("value")}
                        )
        processed_messages.reverse()
        return {"chatHistory": processed_messages}

    def _send_request_get_json(self, method, api_url, **kwargs):
        try:
            # `requests` 모듈의 메서드를 동적으로 선택
            request_method = getattr(requests, method.lower(), None)
            if request_method is None:
                raise ValueError("Invalid method")

            # 요청 보내기
            response = request_method(api_url, headers=self.headers, **kwargs)

            # 응답 상태 코드 확인
            response.raise_for_status()

            res = response.json()

            return res

        except requests.exceptions.RequestException as e:
            print(e)

    def fetch_user_chat_ids(self, start_date, limit):
        """
        특정 날짜로부터 2주간의 user_chat_id를 중복 없이 가져옵니다.
        Args:
            start_date (str): 조회 종료 날짜 (형식: YYYY-MM-DD).
            limit (int): 가져올 최대 user_chat_id 수 (최대 200개).
        Returns:
            list: 중복 없는 user_chat_id 리스트.
        """
        # 날짜 계산: start_date를 기준으로 2주 전의 날짜를 계산
        start_date_iso = datetime.strptime(start_date, "%Y-%m-%d").strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        end_date = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=14)
        end_date_iso = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        # API 요청 URL 및 초기 파라미터 설정
        url = f"{self.base_url}/open/v5/user-chats"
        params = {
            "startDate": end_date_iso,
            "endDate": start_date_iso,
            "state": "closed",
            "limit": 500,
        }

        all_chat_ids = set()  # 중복 제거를 위한 set
        next_cursor = None  # 페이징 처리를 위한 cursor

        while len(all_chat_ids) < limit:
            if next_cursor:
                params["since"] = next_cursor

            try:
                # API 요청
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                # user_chat_id 추출
                user_chats = data.get("userChats", [])
                for chat in user_chats:
                    all_chat_ids.add(chat["id"])
                    if len(all_chat_ids) >= limit:
                        break  # 제한 개수에 도달하면 종료

                # 다음 페이지 설정
                next_cursor = data.get("next")
                if not next_cursor:  # 더 이상 가져올 데이터가 없으면 종료
                    break

            except requests.exceptions.RequestException as e:
                print(f"API 요청 중 오류 발생: {e}")
                break

        return list(all_chat_ids)
