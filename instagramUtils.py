import logging
import os
import re
import discord

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import (
    ClientConnectionError,
    ClientForbiddenError,
    ClientLoginRequired,
    ClientThrottledError,
    GenericRequestError,
    PleaseWaitFewMinutes,
    RateLimitError,
    SentryBlock,
    BadPassword,
)
from requests.exceptions import ProxyError
from urllib3.exceptions import HTTPError

import CustomErrors

# 디스코드로 에러 전송 (봇)
def send_error_to_discord(error_message):
    # 환경변수 가져오기
    load_dotenv()
    bot_token = os.environ.get("BOT_TOKEN")
    channel_id = os.environ.get("CHANNEL_ID")

    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        channel = client.get_channel(int(channel_id))
        if channel:
            await channel.send(error_message)
            await client.close()
        else:
            print("디스코드 채널을 찾을 수 없습니다")

    client.run(bot_token)

def remove_special_characters_using_regex(input_string):
    # 정규표현식으로 특수 문자 제거
    pattern = r"[^\w\s]"
    result_string = re.sub(pattern, "", input_string)
    return result_string

class InstagramUtils:
    """인스타그램 데이터 수집을 위한 유틸 클래스"""
    load_dotenv()

    # 로거 설정
    logger = logging.getLogger()

    cl = Client()
    cl.delay_range = [1, 2]

    # 인스타그램 로그인
    INSTA_ID = os.environ.get("INSTA_ID")
    INSTA_PW = os.environ.get("INSTA_PW")
    NEXT_INSTA_ID = os.environ.get("NEXT_INSTA_ID")
    NEXT_INSTA_PW = os.environ.get("NEXT_INSTA_PW")

    try:
        cl.login(INSTA_ID, INSTA_PW)
    # 로그인 에러 발생 시 디스코드 봇 전송 및 다른 ID로 재로그인 시도 (재로그인 함수로 모듈화 필요)
    except (ProxyError, HTTPError, GenericRequestError, ClientConnectionError, ): # Network level
        send_error_to_discord("Network error")
        cl.logout()
        cl.login(NEXT_INSTA_ID, NEXT_INSTA_PW)
    except (SentryBlock, RateLimitError, ClientThrottledError): # Instagram limit level
        send_error_to_discord("Instagram limit error")
        cl.logout()
        cl.login(NEXT_INSTA_ID, NEXT_INSTA_PW)
    except (ClientLoginRequired, PleaseWaitFewMinutes, ClientForbiddenError): # Logical level
        send_error_to_discord("Logical error")
        cl.logout()
        cl.login(NEXT_INSTA_ID, NEXT_INSTA_PW)
    except (BadPassword): # password error
        send_error_to_discord("password error")
        cl.logout()
        cl.login(NEXT_INSTA_ID, NEXT_INSTA_PW)
    except Exception as e:
        send_error_to_discord(e)
        cl.logout()
        cl.login(NEXT_INSTA_ID, NEXT_INSTA_PW)
        raise e

    cl.dump_settings("session.json")

    logger.info("Instagram Login %s" % INSTA_ID)
    print("login - ", INSTA_ID)

    def re_login(self):
        """
        재 로그인
        :return:
        """
        self.cl.login(self.INSTA_ID, self.INSTA_PW)
        self.cl.dump_settings("session.json")
        self.logger.info("Instagram Login %s" % self.INSTA_ID)

    def post_by_user(self, user_name):
        """
        사용자 이름을 통한 게시글 조회
        :param user_name:
        :return: text: [str]
        """
        try:
            user_info = self.cl.user_info_by_username(user_name)
            isPirvate = user_info.is_private
            isNoPost = user_info.media_count == 0

            if isPirvate:
                raise CustomErrors.PrivateAccountError("비공개 계정입니다.")
            if isNoPost:
                raise CustomErrors.NoPostError("게시물이 없습니다.")
        except ClientLoginRequired as e:
            raise e
        except CustomErrors.CustomError as e:
            raise e
        except Exception as e:
            raise CustomErrors.NoAccountError("존재하지 않는 계정입니다.")

        # 인스타 게시물 수 by username(id)
        media_count = self.cl.user_info_by_username(user_name).media_count
        media_count = 30 if media_count > 30 else media_count

        # user_name으로 userid(int) 가져오기
        user_id = int(self.cl.user_id_from_username(user_name))

        # 게시물 추출
        all_text = ""

        posts = self.cl.user_medias(user_id, media_count)
        for post in posts:
            all_text += post.caption_text

        all_text = remove_special_characters_using_regex(all_text)
        return [all_text.replace("\n", "")]


