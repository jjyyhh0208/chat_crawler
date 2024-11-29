import openpyxl


class ChatExcelSaver:
    """채팅 데이터를 엑셀 파일로 저장하는 클래스"""

    def __init__(self, output_file):
        self.output_file = output_file
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active
        self.ws.title = "Chat History"
        # 헤더 수정: AI 답변 열 추가
        self.ws.append(["질문", "상담사 답변", "AI 답변"])

    def save_to_excel(self, chat_data):
        """
        채팅 데이터를 엑셀에 한 행씩 저장.
        Args:
            chat_data (dict): 채팅 데이터.
        """
        chat_history = chat_data.get("chatHistory", [])

        # user, manager, ai 메시지를 저장할 변수
        user_messages = []
        manager_messages = []
        ai_messages = []

        for chat in chat_history:
            sender = chat["sender"]
            message = chat["message"]

            # sender에 따라 메시지 분류
            if sender == "user":
                user_messages.append(message)
            elif sender == "manager":
                manager_messages.append(message)
            # elif sender == "bot":
            #     ai_messages.append(message)

        # 메시지 연결 (줄바꿈 추가)
        user_cell = "\n\n".join(user_messages)
        manager_cell = "\n\n".join(manager_messages)
        ai_cell = "\n\n".join(ai_messages)

        # 한 행에 저장
        if (
            user_messages or manager_messages or ai_messages
        ):  # 셋 중 하나라도 메시지가 있는 경우만 저장
            self.ws.append([user_cell, manager_cell, ai_cell])

    def save_file(self):
        """엑셀 파일 저장"""
        self.wb.save(self.output_file)
        print(f"엑셀 파일이 저장되었습니다: {self.output_file}")
