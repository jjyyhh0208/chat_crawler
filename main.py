from channel_talk import ChannelTalk
from excel_saver import ChatExcelSaver


def main():
    #########################################################
    # 긁어오고자 하는 채널의 API 키 정보로 수정 필요
    ACCESS_KEY = "67493be6de09b0422090"
    ACCESS_SECRET = "50963eb6ec31afbd5f474855294e7751"
    OUTPUT_FILE = "/Users/0heon_j/Desktop/chat_history.xlsx"
    START_DATE = "2024-11-29"  # 기준 날짜 2주전까지 200개 가져오기
    #########################################################

    try:
        # ChannelTalk 인스턴스 생성
        channel = ChannelTalk(
            user_chat_id=None, x_access_key=ACCESS_KEY, x_access_secret=ACCESS_SECRET
        )

        # 최근 2주간 user_chat_id 가져오기
        user_chat_ids = channel.fetch_user_chat_ids(START_DATE, 200)

        print(f"가져온 user_chat_id 리스트: {user_chat_ids}")
        print(f"user_chat_ids 개수: {len(user_chat_ids)}")

        saver = ChatExcelSaver(OUTPUT_FILE)

        # 각 채팅방 데이터를 가져와 엑셀에 저장
        for user_chat_id in user_chat_ids:
            print(f"현재 처리 중인 user_chat_id: {user_chat_id}")

            channel.user_chat_id = user_chat_id
            chat_history = channel.get_user_chat_messages(order="asc", limit=25)

            # 채팅 데이터를 엑셀에 저장
            saver.save_to_excel(chat_history)

        # 엑셀 파일 저장
        saver.save_file()
        print(f"엑셀 파일이 저장되었습니다: {OUTPUT_FILE}")

    except Exception as e:
        print(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
