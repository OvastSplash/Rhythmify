# 🎵 Rhythmify

**Rhythmify** is a powerful platform for music analytics and personalization that brings your favorite streaming services together into one convenient interface. The project allows you not only to track listening statistics but also to discover new music based on your unique tastes.

---

## ✨ Features

- **Spotify Integration**: Full synchronization with your Spotify account (tracks, playlists, artists).
- **Deep Analytics**: View statistics for your favorite tracks, artists, and genres over different time periods.
- **Smart Recommendations**: A music recommendation system based on your preferences, using Spotify algorithms and Last.fm data.
- **Playlist Management**: Create and edit playlists directly from the application interface.
- **Multi-platform Support**: Integration with Spotify, Deezer, and Last.fm APIs for the most accurate data collection.
- **Background Processing**: Uses Celery for asynchronous data updates without slowing down the user interface.

---

## 🚀 Tech Stack

- **Backend**: Python 3.10+, Django 5.1
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis / RabbitMQ
- **Auth**: Spotify OAuth2
- **External APIs**: Spotify Web API, Last.fm API, Deezer API
- **Testing**: Pytest

---

## 🛠️ Installation and Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Rhythmify.git
cd Rhythmify
```

### 2. Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # For Linux/macOS
# or
venv\Scripts\activate     # For Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root and add the following variables:
```env
DEBUG=True
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/rhythmify
CELERY_BROKER_URL=redis://localhost:6379/0  # or amqp://guest:guest@localhost:5672// for RabbitMQ
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8000/callback/
```

### 5. Database migrations
```bash
python manage.py migrate
```

### 6. Run the project
```bash
# Run Django in one terminal
python manage.py runserver

# Run Celery worker in another terminal
celery -A Rhythmify worker -l info

# (Optional) Run Celery beat for periodic tasks
celery -A Rhythmify beat -l info
```

---

## 📂 Project Structure

- **Main**: Core logic for displaying tops and recommendations.
- **SpotifyController**: Core of Spotify API integration, data management, and aggregation.
- **User**: User management, custom user model, and authentication.
- **Profile**: User dashboard with detailed statistics.
- **LastFM / Deezer**: Modules for integration with respective services.
- **Catalog**: Browsing and searching the music library.

---

## 🧪 Testing
To run tests, use:
```bash
pytest
```

---

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contacts
If you have any questions or suggestions, please create an **Issue** or contact the author directly.

---
*Developed with ❤️ by [obscurum](https://github.com/obscurum)*
