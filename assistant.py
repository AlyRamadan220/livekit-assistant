import asyncio
import os

from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli, room_io
from livekit.agents.llm import (
    ChatContext,
    ChatMessage,
    ImageContent,
)
from livekit.plugins import deepgram, google, silero
from dotenv import load_dotenv

load_dotenv()

REQUIRED_ENV_VARS = [
    "LIVEKIT_URL",
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
    "DEEPGRAM_API_KEY",
    "GOOGLE_API_KEY",
]

SYSTEM_PROMPT = (
    "Your name is Alloy. You are a funny, witty bot. Your interface with users will be voice and vision."
    "Respond with short and concise answers. Avoid using unpronouncable punctuation or emojis."
)


def validate_environment() -> None:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        missing_list = ", ".join(missing)
        raise RuntimeError(
            "Missing required environment variables: "
            f"{missing_list}. Set them before starting the assistant."
        )


async def get_video_track(room: rtc.Room):
    """Get the first video track from the room. We'll use this track to process images."""
    while room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
        for _, participant in room.remote_participants.items():
            for _, track_publication in participant.track_publications.items():
                if track_publication.track is not None and isinstance(
                    track_publication.track, rtc.RemoteVideoTrack
                ):
                    print(f"Using video track {track_publication.track.sid}")
                    return track_publication.track

        await asyncio.sleep(0.2)

    raise RuntimeError("Disconnected before a remote video track was available")


async def entrypoint(ctx: JobContext):
    session = agents.AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=google.LLM(model="gemini-flash-lite-latest"),
        tts=deepgram.TTS(),
    )

    agent = agents.Agent(instructions=SYSTEM_PROMPT)
    latest_image: rtc.VideoFrame | None = None

    async def text_input_cb(sess: agents.AgentSession, ev: room_io.TextInputEvent) -> None:
        await sess.interrupt()
        content: list[str | ImageContent] = [ev.text]
        if latest_image is not None:
            content.append(ImageContent(image=latest_image))
        sess.generate_reply(user_input=ChatMessage(role="user", content=content))

    await session.start(
        agent,
        room=ctx.room,
        record=False,
        room_options=room_io.RoomOptions(
            text_input=room_io.TextInputOptions(text_input_cb=text_input_cb),
            video_input=True,
        ),
    )

    print(f"Room name: {ctx.room.name}")

    session.say("Hi there! How can I help?", allow_interruptions=True)

    while ctx.room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
        video_track = await get_video_track(ctx.room)

        async for event in rtc.VideoStream(video_track):
            # We'll continually grab the latest image from the video track
            # and store it in a variable.
            latest_image = event.frame


if __name__ == "__main__":
    validate_environment()
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
