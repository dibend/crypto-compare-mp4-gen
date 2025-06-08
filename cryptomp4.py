import gradio as gr
import matplotlib.pyplot as plt
from matplotlib import style
import requests
import time
import datetime
import random
import io
from PIL import Image
import tempfile
import os
import logging
import numpy as np
import subprocess
import configparser
from pydub import AudioSegment
from pydub.generators import Sine

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Configuration Loading ---
config = configparser.ConfigParser()
# Ensure the script can find config.ini even if run from a different directory
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, 'config.ini')

if not os.path.exists(config_path):
    logger.error(f"CRITICAL: config.ini not found at {config_path}. Please create it.")
    # You might want to exit or handle this more gracefully
    exit()

config.read(config_path)


API_KEY = config.get(
    'DEFAULT',
    'API_KEY',
    fallback="YOUR_CRYPTOCOMPARE_API_KEY_GOES_HERE"
)
FFMPEG_EXECUTABLE_PATH = config.get(
    'DEFAULT', 'FFMPEG_EXECUTABLE_PATH', fallback="ffmpeg"
)

# --- FFmpeg Path Validation ---
if FFMPEG_EXECUTABLE_PATH and FFMPEG_EXECUTABLE_PATH != "ffmpeg":
    if not (os.path.exists(FFMPEG_EXECUTABLE_PATH) and
            os.path.isfile(FFMPEG_EXECUTABLE_PATH) and
            os.access(FFMPEG_EXECUTABLE_PATH, os.X_OK)):
        logger.warning(
            f"FFMPEG_EXECUTABLE_PATH from config.ini ('{FFMPEG_EXECUTABLE_PATH}') is invalid. "
            "Falling back to 'ffmpeg' in system PATH."
        )
        FFMPEG_EXECUTABLE_PATH = "ffmpeg"
else:
    FFMPEG_EXECUTABLE_PATH = "ffmpeg"

logger.info(f"Using FFmpeg executable: {FFMPEG_EXECUTABLE_PATH}")
if API_KEY == "YOUR_CRYPTOCOMPARE_API_KEY_GOES_HERE":
    logger.error("CRITICAL: API_KEY is not set in config.ini. Data fetching will fail.")
else:
    logger.debug(f"API key loaded: {API_KEY[:4]}****")

# --- Matplotlib Configuration ---
style.use("bmh")
plt.rcParams['figure.figsize'] = [10, 7]
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.family'] = 'sans-serif'
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# --- Global Constants ---
BASE_CURRENCY = "USD"
AVAILABLE_CRYPTOS = [
    "BTC", "ETH", "XRP", "LTC", "ADA", "SOL", "DOGE", "DOT", "SHIB",
    "AVAX", "MATIC", "TRX", "ETC", "XMR", "RVN", "KAS"
]
PLOT_COLORS = [
    "#FF6347", "#4682B4", "#32CD32", "#FFD700", "#DA70D6", "#FFA500",
    "#00CED1", "#8A2BE2", "#FF4500", "#1E90FF"
]

def fetch_crypto_data(crypto_symbol, limit_days=365):
    """Fetches historical daily price data for a cryptocurrency."""
    logger.info(f"Fetching crypto data for {crypto_symbol}, limit {limit_days} days.")
    all_prices, all_timestamps = [], []

    if API_KEY == "YOUR_CRYPTOCOMPARE_API_KEY_GOES_HERE":
        logger.error("API_KEY not set in config.ini.")
        return [], []

    points_to_fetch = limit_days
    current_timestamp = int(time.time())

    while points_to_fetch > 0:
        api_call_limit = min(points_to_fetch, 2000)
        url = (
            f"https://min-api.cryptocompare.com/data/v2/histoday?"
            f"fsym={crypto_symbol}&tsym={BASE_CURRENCY}"
            f"&limit={api_call_limit}&toTs={current_timestamp}&api_key={API_KEY}"
        )

        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {crypto_symbol}: {e}")
            return [], []

        if data.get("Response") == "Error" or "Data" not in data or not data["Data"].get("Data"):
            logger.warning(f"API returned no data for {crypto_symbol}. Message: {data.get('Message')}")
            break

        daily_data = data["Data"]["Data"]
        prices_chunk = [item['close'] for item in daily_data]
        timestamps_chunk = [item['time'] for item in daily_data]

        all_prices = prices_chunk + all_prices
        all_timestamps = timestamps_chunk + all_timestamps
        points_to_fetch -= len(daily_data)

        if len(daily_data) < api_call_limit:
            logger.info("End of available history reached.")
            break

        current_timestamp = data["Data"]["TimeFrom"] - 1
        time.sleep(0.2)

    final_prices = all_prices[-limit_days:]
    final_timestamps = all_timestamps[-limit_days:]
    formatted_dates = [datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in final_timestamps]
    logger.info(f"Finished fetching {crypto_symbol}. Got {len(final_prices)} data points.")
    return formatted_dates, final_prices

def _generate_single_crypto_mp4(crypto_symbol, limit_days=365, status_update_fn=None):
    """Generates a single MP4 video using direct ffmpeg calls."""
    if status_update_fn is None:
        status_update_fn = logger.info

    status_update_fn(f"Fetching data for {crypto_symbol}...")
    dates_str, prices_numeric = fetch_crypto_data(crypto_symbol, limit_days)

    if not dates_str:
        status_update_fn(f"Failed to fetch data for {crypto_symbol}.")
        return None

    temp_dir_obj = tempfile.TemporaryDirectory(prefix=f"crypto_{crypto_symbol}_")
    temp_dir_path = temp_dir_obj.name

    try:
        status_update_fn(f"Generating frames for {crypto_symbol}...")
        fig, ax = plt.subplots()
        fig.text(0.5, 0.5, "NJtek.net", fontsize=50, color='gray', alpha=0.15, ha='center', va='center', rotation=30, zorder=0)
        color_idx = AVAILABLE_CRYPTOS.index(crypto_symbol) % len(PLOT_COLORS) if crypto_symbol in AVAILABLE_CRYPTOS else 0
        line, = ax.plot([], [], label=f"{crypto_symbol} Price", color=PLOT_COLORS[color_idx], linewidth=2.0)
        ax.set_xlabel("Date")
        ax.set_ylabel(f"Price ({BASE_CURRENCY})")
        ax.legend(loc='upper left')
        ax.grid(True, linestyle=':', alpha=0.5)

        num_ticks = min(len(dates_str), 10)
        tick_spacing = max(1, len(dates_str) // num_ticks if num_ticks > 0 else 1)
        ax.set_xticks(range(0, len(dates_str), tick_spacing))
        ax.set_xticklabels([dates_str[i] for i in range(0, len(dates_str), tick_spacing)], rotation=30, ha="right")
        date_artist = fig.text(0.5, 0.96, '', ha="center", va="top", fontweight='bold')
        fig.tight_layout(rect=[0.05, 0.08, 0.95, 0.92])

        frame_paths = []
        animation_step = max(1, len(dates_str) // 100)
        frame_indices = list(range(0, len(dates_str), animation_step))
        if len(dates_str) > 0 and (len(dates_str) - 1) not in frame_indices:
            frame_indices.append(len(dates_str) - 1)

        for i, data_idx in enumerate(frame_indices):
            prices_so_far = prices_numeric[:data_idx + 1]
            line.set_data(range(len(prices_so_far)), prices_so_far)
            ax.set_xlim(0, max(0, len(dates_str) - 1))
            ax.set_ylim(min(prices_so_far) * 0.9, max(prices_so_far) * 1.1)
            date_artist.set_text(f"{crypto_symbol} | {dates_str[data_idx]} | Price: {prices_numeric[data_idx]:.2f} {BASE_CURRENCY}")
            frame_path = os.path.join(temp_dir_path, f"frame_{i:04d}.png")
            fig.savefig(frame_path)
            frame_paths.append(frame_path)
        plt.close(fig)

        status_update_fn(f"Synthesizing audio for {crypto_symbol}...")
        base_time_ms = 5000 + max(0, (len(frame_paths) - 100) * 30)
        last_frame_ms = 3000
        normal_dur_ms = max(20, base_time_ms // (len(frame_paths) - 1 or 1))
        durations = [normal_dur_ms] * (len(frame_paths) - 1) + [last_frame_ms]

        min_price, max_price = min(prices_numeric), max(prices_numeric)
        price_range = max_price - min_price
        audio_segments = []
        
        for i, data_idx in enumerate(frame_indices):
            price = prices_numeric[data_idx]
            norm_price = (price - min_price) / price_range if price_range > 1e-6 else 0.5
            freq = 220 + (norm_price * (880 - 220))
            segment = Sine(freq).to_audio_segment(duration=durations[i], volume=-12).fade_in(15).fade_out(15)
            audio_segments.append(segment)

        combined_audio = sum(audio_segments, AudioSegment.empty())
        audio_path = os.path.join(temp_dir_path, "audio.wav")
        if combined_audio.duration_seconds > 0:
            combined_audio.export(audio_path, format="wav")
        else:
            audio_path = None

        status_update_fn(f"Compiling video for {crypto_symbol}...")
        concat_list_path = os.path.join(temp_dir_path, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            for i, frame_path in enumerate(frame_paths):
                safe_path = frame_path.replace('\\', '/')
                f.write(f"file '{safe_path}'\n")
                f.write(f"duration {durations[i] / 1000:.6f}\n")

        output_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        cmd = [FFMPEG_EXECUTABLE_PATH, '-f', 'concat', '-safe', '0', '-i', concat_list_path]
        if audio_path:
             cmd.extend(['-i', audio_path, '-c:a', 'aac', '-b:a', '192k'])
        else:
            cmd.extend(['-an'])
        cmd.extend(['-c:v', 'libx264', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-shortest', '-y', output_mp4])

        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        return output_mp4

    except Exception as e:
        logger.error(f"Failed during generation for {crypto_symbol}: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            logger.error(f"FFmpeg stderr: {e.stderr}")
        return None
    finally:
        temp_dir_obj.cleanup()

def generate_animations_for_gallery(selected_cryptos, fetch_all_history):
    """Wrapper function to generate videos for the Gradio UI."""
    # This function now yields status updates for the UI
    days_to_fetch = 20000 if fetch_all_history else 365
    total_selected = len(selected_cryptos)
    
    if not total_selected:
        yield "Please select at least one cryptocurrency.", []
        return

    yield "Starting generation process...", None

    all_paths = []
    for i, crypto in enumerate(selected_cryptos):
        yield f"Processing {i+1}/{total_selected}: {crypto}...", all_paths
        
        path = _generate_single_crypto_mp4(crypto, days_to_fetch, logger.info)
        
        if path:
            all_paths.append(path)
            yield f"Finished {i+1}/{total_selected}: {crypto}", all_paths
        else:
            yield f"Failed {i+1}/{total_selected}: {crypto}. Check logs.", all_paths

    if not all_paths:
        final_status = "Failed to generate any videos. Check console for errors."
    elif len(all_paths) < total_selected:
        final_status = f"Completed. Generated {len(all_paths)} of {total_selected} videos."
    else:
        final_status = "All videos generated successfully!"
        
    yield final_status, all_paths

# --- Gradio Interface ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="orange")) as demo:
    gr.Markdown("# 📈 Crypto Price Animator (MP4 with Synced Audio)")
    with gr.Row():
        crypto_selector = gr.CheckboxGroup(choices=AVAILABLE_CRYPTOS, label="Select Cryptocurrencies", value=["BTC", "ETH"])
    with gr.Row():
        fetch_all_history_cb = gr.Checkbox(label="Fetch all available history (can be very slow)", value=False)
    
    with gr.Row():
        generate_btn = gr.Button("🚀 Generate Animated Plot(s) (MP4)", variant="primary")

    status_box = gr.Textbox(label="Status", interactive=False, placeholder="Awaiting generation...")
    output_gallery = gr.Gallery(label="🎞️ Animated Price Charts", columns=1, object_fit="contain", show_label=False)

    generate_btn.click(
        fn=generate_animations_for_gallery,
        inputs=[crypto_selector, fetch_all_history_cb],
        outputs=[status_box, output_gallery]
    )

if __name__ == "__main__":
    # Add a check for the config file on startup
    if not os.path.exists('config.ini'):
         logger.error("FATAL: config.ini not found. Please create it with your API_KEY and FFMPEG_EXECUTABLE_PATH.")
    else:
        logger.info("Starting Gradio Crypto Animator App.")
        demo.launch(share=True, debug=True)
