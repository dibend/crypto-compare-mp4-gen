<h1 align="center">📈 Crypto Compare MP4 Generator 📉</h1>

<p align="center">
  <strong>A Python-based tool by <a href="https://github.com/Dibend">@Dibend</a> with a Gradio web interface to generate animated MP4 videos of cryptocurrency price history with synchronized audio.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/Gradio-4.x-orange?style=for-the-badge&logo=gradio" alt="Gradio Version">
  <img src="https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge" alt="License: GPL v3">
  <img src="https://img.shields.io/badge/FFmpeg-Required-red?style=for-the-badge&logo=ffmpeg" alt="FFmpeg Required">
</p>

<hr>

<h2>🌟 Features</h2>
<ul>
  <li><strong>🌐 Web-Based Interface</strong>: Easy-to-use Gradio interface for selecting cryptocurrencies and generation options.</li>
  <li><strong>💹 Multiple Cryptocurrencies</strong>: Select from a list of popular cryptocurrencies to generate animations for.</li>
  <li><strong>📊 Historical Data</strong>: Fetches historical price data from the CryptoCompare API.</li>
  <li><strong>🎬 MP4 Video Generation</strong>: Creates high-quality MP4 videos of the price chart animation.</li>
  <li><strong>🎵 Synchronized Audio</strong>: Generates a sine wave audio track where the frequency corresponds to the cryptocurrency's price.</li>
  <li><strong>⚙️ Customizable History</strong>: Choose between a 365-day history or the entire available price history.</li>
  <li><strong>🖼️ Matplotlib Visualization</strong>: Uses Matplotlib for clear and professional-looking plots.</li>
  <li><strong>🛠️ Flexible Configuration</strong>: Easily configure your API key and FFmpeg path.</li>
</ul>

<hr>

<h2>🎥 Demo</h2>
<p>Below is a placeholder for a sample generated video. The actual output will be an MP4 file showing the price chart animating over time with corresponding audio.</p>

<p align="center">
  <img src="https://i.imgur.com/SAMPLE.gif" alt="Sample Animation" width="600">
</p>

<hr>

<h2>📋 Prerequisites</h2>
<p>Before you begin, ensure you have the following installed:</p>
<ul>
  <li><strong>Python 3.7+</strong></li>
  <li><strong>pip</strong> (Python package installer)</li>
  <li><strong>FFmpeg</strong>: This is a crucial dependency for video and audio processing. You can download it from the <a href="https://ffmpeg.org/download.html">official FFmpeg website</a>. Make sure the <code>ffmpeg</code> executable is in your system's PATH or provide the path in the <code>config.ini</code> file.</li>
</ul>

<hr>

<h2>🚀 Installation</h2>
<ol>
  <li>
    <strong>Clone the repository:</strong>
    <pre><code>git clone https://github.com/Dibend/crypto-compare-mp4-gen.git
cd crypto-compare-mp4-gen</code></pre>
  </li>
  <li>
    <strong>Install the required Python libraries:</strong>
    <p>A <code>requirements.txt</code> file is recommended for easier installation.</p>
    <strong><code>requirements.txt</code></strong>
    <pre><code>gradio
matplotlib
requests
pydub
numpy</code></pre>
    <p>Install the dependencies using pip:</p>
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
</ol>

<hr>

<h2>⚙️ Configuration</h2>
<ol>
  <li>
    <strong>Create the <code>config.ini</code> file:</strong>
    <p>In the same directory as the script, create a file named <code>config.ini</code>.</p>
  </li>
  <li>
    <strong>Add your API Key and FFmpeg Path:</strong>
    <p>You will need a free API key from <a href="https://min-api.cryptocompare.com/">CryptoCompare</a>.</p>
    <strong><code>config.ini</code></strong>
    <pre><code>[DEFAULT]
API_KEY = YOUR_CRYPTOCOMPARE_API_KEY_GOES_HERE
FFMPEG_EXECUTABLE_PATH = ffmpeg</code></pre>
    <ul>
      <li><code>API_KEY</code>: Your CryptoCompare API key.</li>
      <li><code>FFMPEG_EXECUTABLE_PATH</code>: The path to your FFmpeg executable. If <code>ffmpeg</code> is in your system's PATH, you can leave it as <code>ffmpeg</code>. Otherwise, provide the full path (e.g., <code>C:/ffmpeg/bin/ffmpeg.exe</code> on Windows).</li>
    </ul>
  </li>
</ol>

<hr>

<h2>▶️ How to Run</h2>
<p>Once you have completed the installation and configuration, you can run the application with the following command:</p>
<pre><code>python your_script_name.py</code></pre>
<p>This will launch the Gradio web interface. Open the provided URL (usually <code>http://127.0.0.1:7860</code>) in your web browser to start using the Crypto Compare MP4 Generator.</p>

<hr>

<h2>🧠 How It Works</h2>
<details>
  <summary><strong>Click to expand and see the code overview</strong></summary>
  <ul>
    <li><code>fetch_crypto_data</code>: This function connects to the CryptoCompare API to download historical daily price data for a specified cryptocurrency.</li>
    <li><code>_generate_single_crypto_mp4</code>: This is the core function for generating a single video. It performs the following steps:
      <ol>
        <li>Fetches the crypto data using <code>fetch_crypto_data</code>.</li>
        <li>Uses Matplotlib to generate individual frames of the price chart animation.</li>
        <li>Utilizes <code>pydub</code> to synthesize a sine wave audio track where the pitch is mapped to the price.</li>
        <li>Calls the FFmpeg command-line tool to stitch the frames and the audio together into an MP4 video.</li>
      </ol>
    </li>
    <li><code>generate_animations_for_gallery</code>: This function serves as a wrapper for the Gradio interface. It iterates through the selected cryptocurrencies and calls <code>_generate_single_crypto_mp4</code> for each, yielding status updates to the UI.</li>
    <li><strong>Gradio Interface</strong>: The script uses the Gradio library to create an interactive web-based user interface, allowing users to easily select their desired options and generate the animations.</li>
  </ul>
</details>

<hr>

<h2>🌐 Compatibility</h2>
<details>
  <summary><strong>Click to expand for compatibility details</strong></summary>
  <h3>Operating Systems</h3>
  <p>This script is designed to be cross-platform and should work on the following operating systems, provided Python and FFmpeg are installed and configured correctly:</p>
  <ul>
    <li><strong>Windows</strong>: The script includes a check for Windows to suppress the console window when running FFmpeg.</li>
    <li><strong>macOS</strong>: Fully compatible.</li>
    <li><strong>Linux</strong>: Fully compatible.</li>
  </ul>
  <h3>Browsers</h3>
  <p>The Gradio interface is web-based and is compatible with modern web browsers, including:</p>
  <ul>
    <li>Google Chrome</li>
    <li>Mozilla Firefox</li>
    <li>Safari</li>
    <li>Microsoft Edge</li>
  </ul>
  <h3>FFmpeg</h3>
  <p>The most common compatibility issue is with the FFmpeg executable path. The script first checks for the path specified in <code>config.ini</code>. If that path is invalid or not provided, it falls back to trying to use <code>ffmpeg</code> from the system's PATH.</p>
  <strong>To ensure compatibility:</strong>
  <ul>
    <li><strong>Recommended</strong>: Add the directory containing <code>ffmpeg</code> to your system's PATH environment variable.</li>
    <li><strong>Alternative</strong>: Provide the full, direct path to the <code>ffmpeg</code> executable in the <code>config.ini</code> file.</li>
  </ul>
</details>

<hr>

<h2>🔧 Troubleshooting</h2>
<details>
  <summary><strong>Click to expand for common issues and solutions</strong></summary>
  <ul>
    <li><strong><code>CRITICAL: config.ini not found</code></strong>: Ensure you have created the <code>config.ini</code> file in the same directory as the Python script.</li>
    <li><strong><code>CRITICAL: API_KEY is not set in config.ini</code></strong>: Make sure you have added your CryptoCompare API key to the <code>config.ini</code> file.</li>
    <li><strong>Video generation fails or FFmpeg error</strong>: This is likely due to an incorrect FFmpeg path. Double-check the <code>FFMPEG_EXECUTABLE_PATH</code> in your <code>config.ini</code> or ensure <code>ffmpeg</code> is in your system's PATH.</li>
    <li><strong><code>requests.exceptions.RequestException</code></strong>: This indicates a problem with the API request. Check your internet connection and ensure the CryptoCompare API is accessible.</li>
    <li><strong>Slow performance with "Fetch all available history"</strong>: This option can download a large amount of data and take a significant amount of time and resources to process. This is expected behavior.</li>
  </ul>
</details>

<hr>

<h2>🤝 Contributing</h2>
<p>Contributions are welcome! If you would like to contribute to this project, please follow these steps:</p>
<ol>
  <li>Fork the repository.</li>
  <li>Create a new branch (<code>git checkout -b feature/your-feature-name</code>).</li>
  <li>Make your changes.</li>
  <li>Commit your changes (<code>git commit -m 'Add some feature'</code>).</li>
  <li>Push to the branch (<code>git push origin feature/your-feature-name</code>).</li>
  <li>Open a pull request.</li>
</ol>

<hr>

<h2>📜 License</h2>
<p>This project is licensed under the terms of the <strong>GNU General Public License v3.0</strong>. For the full license text, please see the <code>LICENSE</code> file or visit <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank" rel="noopener noreferrer">the official GNU website</a>.</p>

