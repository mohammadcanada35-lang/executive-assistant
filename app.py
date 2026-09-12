def recv(self, frame):
    try:
        pcm_data = convert_to_16khz(frame)

        if not audio_to_gemini.full():
            audio_to_gemini.put_nowait(pcm_data)

    except Exception:
        pass

    try:
        out_bytes = audio_from_gemini.get_nowait()

        out_array = np.frombuffer(
            out_bytes,
            dtype=np.int16
        )

        out_array = out_array.reshape(1, -1)

        new_frame = av.AudioFrame.from_ndarray(
            out_array,
            format="s16",
            layout="mono"
        )

        new_frame.sample_rate = 24000

        return new_frame

    except queue.Empty:
        silence = np.zeros(
            (1, frame.samples),
            dtype=np.int16
        )

        silent_frame = av.AudioFrame.from_ndarray(
            silence,
            format="s16",
            layout="mono"
        )

        silent_frame.sample_rate = frame.sample_rate

        return silent_frame
