from pathlib import Path

import httpx
from aiofile import async_open
from botoy import AsyncAction, GroupMsg
from botoy import async_decorators as deco
from botoy import jconfig, logger
from botoy.collection import MsgTypes
from botoy.parser import group as gp
from tenacity import AsyncRetrying, RetryError, retry, stop_after_attempt, wait_random

curFileDir = Path(__file__).parent  # 当前文件路径

__doc__ = "download group files"
config = jconfig.get_configuration("autoDownloadGroupFiles")
groups = config.get("groups")
download_path = (
    Path(config.get("downloadPath"))
    if config.get("downloadPath")
    else (curFileDir / "files")
)

logger.warning(f"downloadGroupFiles:监听群组:{groups} 下载路径{download_path}")


@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
async def download_files(url, filename):
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as resp:
            async with async_open(download_path / filename, "wb") as f:
                async for chunk in resp.aiter_bytes():
                    await f.write(chunk)


@deco.ignore_botself
@deco.from_these_groups(*groups)
@deco.these_msgtypes(MsgTypes.GroupFileMsg)
async def receive_group_msg(ctx: GroupMsg):
    async with AsyncAction.from_ctx(ctx) as act:
        if file_info := gp.file(ctx):
            logger.warning(f"开始解析:{file_info.FileName}")
            try:
                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(3), wait=wait_random(min=1, max=2)
                ):
                    with attempt:
                        if file_data := await act.getGroupFileURL(
                            ctx.FromGroupId, file_info.FileID
                        ):
                            # print(file_data)
                            logger.warning(f"FileUrl:{file_data['Url']}")
                        else:
                            raise Exception("file_data None")
            except RetryError:
                logger.error(f"文件{file_info.FileName}解析错误")
                return
    try:
        logger.warning(f"开始下载:{file_info.FileName} size:{file_info.FileSize}")
        await download_files(file_data["Url"], file_info.FileName)
    except Exception as e:
        logger.error(f"下载文件:{file_info.FileName}  错误:\r\n{e}")
        return
    logger.success(f"下载文件成功: {file_info.FileName}")
