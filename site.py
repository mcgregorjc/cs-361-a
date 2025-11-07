
from flask import Flask, render_template_string, request, jsonify, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = ''

# stand in for database
MOVIES_FILE = 'movies.json'

def load_movies():
    try:
        if os.path.exists(MOVIES_FILE):
            with open(MOVIES_FILE, 'r') as f:
                data = json.load(f)
                print(f"Loaded {len(data)} movies from {MOVIES_FILE}")
                return data
        else:
            print(f"{MOVIES_FILE} does not exist, creating with sample data")
            return []
    except Exception as e:
        print(f"Error loading movies: {e}")
        return []

def save_movies(movies):
    try:
        with open(MOVIES_FILE, 'w') as f:
            json.dump(movies, f, indent=2)
        print(f"Saved {len(movies)} movies to {MOVIES_FILE}")
    except Exception as e:
        print(f"Error saving movies: {e}")


def init_sample_data():

    sample_movies = [
        {
            "id": 1,
            "title": "Spider-Man: No Way Home",
            "year": 2021,
            "director": "jon Watts",
            "genre": "thriler",
            "rating": 8.2,
            "description": "With Spider-Man's identity now revealed, our friendly neighborhood web-slinger is unmasked and no longer able to separate his normal life as Peter Parker from the high stakes of being a superhero. When Peter asks for help from Doctor Strange, the stakes become even more dangerous, forcing him to discover what it truly means to be Spider-Man."
        },

        {
            "id": 2,
            "title": "Deadpool",
            "year": 2016,
            "director": "Tim Miller",
            "genre": "Action, Comedy",
            "rating": 8,
            "description": "Wade Wilson (Ryan Reynolds) is a former Special Forces operative who now works as a mercenary. His world comes crashing down when evil scientist Ajax (Ed Skrein) tortures, disfigures and transforms him into Deadpool. The rogue experiment leaves Deadpool with accelerated healing powers and a twisted sense of humor. With help from mutant allies Colossus and Negasonic Teenage Warhead (Brianna Hildebrand), Deadpool uses his new skills to hunt down the man who nearly destroyed his life."
        },

        {
            "id": 3,
            "title": "The Dark Knight",
            "year": 2008,
            "director": "Christopher Nolan",
            "genre": "Action, Crime, Drama",
            "rating": 9.1,
            "description": "With the help of allies, Lt. Jim Gordon and DA Harvey Dent, Batman is able to keep a tight lid on crime in Gotham City. But when a young criminal calling himself the Joker suddenly throws the town into chaos, the caped crusader begins to tread a fine line between heroism and vigilantism."
        },

        {
            "id": 4,
            "title": "Batman Beyond: Return of the Joker",
            "year": 2000,
            "director": "Curt geda",
            "genre": "Action, sci-fi",
            "rating": 7.7,
            "description": "In the Gotham City of the future, an older Bruce Wayne (Kevin Conroy) trains a college student, Terry McGinnis (Will Friedle), to replace him as Batman. Meanwhile, the Joker (Mark Hamill) has re-emerged as the leader of the Jokerz, a gang inspired by their evil hero, who was previously thought to be dead. Terry tries to stop the theft of communications gear by the Jokerz, but the Joker narrowly escapes. The truth about the Joker's life and death slowly emerges through violent confrontations."
        },

        {
            "id": 5,
            "title": "Superman",
            "year": 2025,
            "director": "James Gunn",
            "genre": "Action, Adventure",
            "rating": 7.1,
            "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption."
        }
    ]
    save_movies(sample_movies)
    return sample_movies


if not os.path.exists(MOVIES_FILE) or os.path.getsize(MOVIES_FILE) == 0:

    print("Initializing with sample data...")
    init_sample_data()


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Database</title>
    <style>

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            opacity: 0.9;
            font-size: 1.1em;
        }
        

        .info-icon {
            display: inline-block;
            width: 18px;
            height: 18px;
            background: #4CAF50;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 18px;
            font-size: 12px;
            cursor: help;
            margin-left: 5px;
            position: relative;
        }
        
        .info-icon:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            white-space: nowrap;
            font-size: 12px;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .controls {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        
        .control-group {
            margin-bottom: 20px;
        }
        
        .control-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
      
        .search-box {
            width: 100%;
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .search-box:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 10px 24px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        
        .history-controls {
            display: flex;
            gap: 10px;
            align-items: center;
            padding: 15px 30px;
            background: #fff3cd;
            border-bottom: 2px solid #ffc107;
        }
        
        .history-controls button {
            padding: 8px 16px;
            font-size: 14px;
        }
        
        .history-info {
            margin-left: auto;
            color: #856404;
            font-weight: 600;
        }
        
       
        .breadcrumb {

            padding: 13px 30px;
            background: #e7f3ff;
            border-bottom: 2px solid #b3d9ff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .breadcrumb span {
            color: #0066cc;
            font-weight: 600;
        }
        
        
       
        .view-modes {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .view-mode-btn {
            padding: 8px 16px;
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .view-mode-btn.active {
            background: #667eea;
            color: white;
        }
        
        .movies-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        
        .movie-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .movie-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        
        .movie-title {
            font-size: 1.3em;
            font-weight: 700;
            color: #333;
            margin-bottom: 8px;
        }
        
        .movie-meta {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 12px;
        }
        
        .movie-rating {
            display: inline-block;
            background: #ffd700;
            color: #333;
            padding: 4px 10px;
            border-radius: 5px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .movie-description {
            color: #555;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
     
        .movie-card.expanded .movie-description {
            -webkit-line-clamp: unset;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            padding: 20px;
            overflow-y: auto;
        }
        
        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: white;
            border-radius: 15px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .close-btn {
            font-size: 30px;
            cursor: pointer;
            color: #666;
            background: none;
            border: none;
            padding: 0;
            width: 30px;
            height: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input,
        .form-group textarea {

            width: 100%;
            padding: 13px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        
        .form-group textarea {
            resize: vertical;
            min-height: 100px;
        }

        .preview-mode {
            background: #f0f8ff;
            border: 2px dashed #667eea;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        
        .preview-mode h4 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .no-results {
            text-align: center;
            padding: 60px 30px;
            color: #666;
        }
        
        .no-results h2 {
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .movies-grid {
                grid-template-columns: 1fr;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1> Movie database</h1>
            <p class="subtitle">Browse, Search, and Manage Your Movie Colection</p>
        </header>
        
       
        <div class="breadcrumb">
            <span id="current-view">Browsing All Movies</span>
        </div>
        
        
        <div class="history-controls">
            <button class="btn-secondary" onclick="historyUndo()" id="undo-btn" disabled>

                 Undo
            </button>
            <button class="btn-secondary" onclick="historyRedo()" id="redo-btn" disabled>

                 Redo
            </button>
            <button class="btn-secondary" onclick="clearHistory()">

                Clear History
            </button>
            <span class="history-info" id="history-info">No actions yet</span>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="search">

                    Search Movies
                    <span class="info-icon" data-tooltip="Benefit: Quickly find movies by title. time cost: 0">i</span>
                </label>
                <input 
                    type="text" 
                    id="search" 
                    class="search-box" 
                    placeholder="Type movie name to search..."
                    oninput="searchMovies()"
                >
            </div>
            
            <div class="button-group">
                <button class="btn-primary" onclick="showAddMovieModal()">

                     Add New Movie
                    <span class="info-icon" data-tooltip="Benefit: Expand your collection. time cost:  1-2 min">i</span>
                </button>
                <button class="btn-secondary" onclick="showAllMovies()">

                    Show All Movies
                </button>
                <button class="btn-secondary" onclick="sortMovies('rating')">

                    Sort by Rating
                </button>
                <button class="btn-secondary" onclick="sortMovies('year')">

                    Sort by Year
                </button>
            </div>
            
           
            <div class="view-modes">
                <span style="font-weight: 600; color: #333;">View Mode:</span>
                <button class="view-mode-btn active" onclick="setViewMode('grid')" data-mode="grid">

                    Grid View
                </button>
                <button class="view-mode-btn" onclick="setViewMode('list')" data-mode="list">

                    List View
                </button>
                <button class="view-mode-btn" onclick="setViewMode('compact')" data-mode="compact">

                    Compact View
                </button>
            </div>
        </div>
        
        <div class="movies-grid" id="movies-container">
           
        </div>
    </div>
    
    <!-- ad/edit movie--> 

    <div class="modal" id="movie-modal">

        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modal-title">Add New Movie</h2>
                
                <button class="close-btn" onclick="closeModal()">&times;</button>
                
            </div>
            
            <form id="movie-form" onsubmit="saveMovie(event)">
                <div class="form-group">
                    <label>Title *</label>
                    
                    <input type="text" id="movie-title" required>
                </div>
                
                <div class="form-group">
                    <label>Year *</label>
                    <input type="number" id="movie-year" min="1900" max="2030" required>
                </div>
                
                <div class="form-group">
                    <label>Director *</label>
                    <input type="text" id="movie-director" required>
                </div>
                
                <div class="form-group">
                    <label>Genre *</label>
                    
                    <input type="text" id="movie-genre" placeholder="e.g., Action, Drama, Comedy" required>
                </div>
                
                <div class="form-group">
                    <label>Rating (0-10) *</label>
                    <input type="number" id="movie-rating" min="0" max="10" step="0.1" required>
                </div>
                
                <div class="form-group">
                    <label>Description *</label>
                    
                    <textarea id="movie-description" required></textarea>
                </div>
                
                <div class="preview-mode" id="preview-section" style="display: none;">
                
                    <h4>Preview Your Movie Entry:</h4>
                    
                    <div id="preview-content"></div>
                </div>
                
                <div class="button-group">
                    <button type="button" class="btn-secondary" onclick="previewMovie()">
                    
                         Preview
                    </button>
                    <button type="submit" class="btn-primary">
                    
                         Save Movie
                         
                    </button>
                    <button type="button" class="btn-secondary" onclick="closeModal()">
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        let movies = [];
        let filteredMovies = [];
        let currentViewMode = 'grid';
        let history = [];
        let historyIndex = -1;
        let currentEditingId = null;
        
        window.onload = function() {
            loadMovies();
        };
        
        function loadMovies() {
            fetch('/api/movies')
                .then(response => response.json())
                .then(data => {
                    movies = data;
                    filteredMovies = movies;
                    displayMovies();
                    addToHistory('Loaded all movies');
                });
        }
        
        function displayMovies() {
            const container = document.getElementById('movies-container');
            
            if (filteredMovies.length === 0) {
                container.innerHTML = `
                    <div class="no-results">
                        <h2>No movies found</h2>
                        <p>Try adjusting your search or add a new movie!</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = filteredMovies.map(movie => `
                <div class="movie-card" onclick="toggleExpand(this)">
                    <div class="movie-title">${movie.title}</div>
                    <div class="movie-meta">
                        ${movie.year} • ${movie.director}
                    </div>
                    <div class="movie-rating"> ${movie.rating}/10</div>
                    <div class="movie-meta" style="margin-top: 5px;">
                        <strong>Genre:</strong> ${movie.genre}
                    </div>
                    <div class="movie-description" style="margin-top: 10px;">
                        ${movie.description}
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="btn-primary" onclick="editMovie(${movie.id}, event)" style="font-size: 14px; padding: 8px 16px;">
                             Edit
                        </button>
                        <button class="btn-secondary" onclick="deleteMovie(${movie.id}, event)" style="font-size: 14px; padding: 8px 16px; background: #dc3545;">
                             Delete
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        function toggleExpand(card) {
            if (event.target.tagName === 'BUTTON') return;
            card.classList.toggle('expanded');
        }
        
        function searchMovies() {
            const query = document.getElementById('search').value.toLowerCase();
            filteredMovies = movies.filter(movie => 
                movie.title.toLowerCase().includes(query)
            );
            displayMovies();
            
            const breadcrumb = document.getElementById('current-view');
            if (query) {
                breadcrumb.textContent = `Search Results for "${query}"`;
                addToHistory(`Searched for "${query}"`);
            } else {
                breadcrumb.textContent = 'Browsing All Movies';
            }
        }
        
        function showAllMovies() {
            document.getElementById('search').value = '';
            filteredMovies = movies;
            displayMovies();
            document.getElementById('current-view').textContent = 'Browsing All Movies';
            addToHistory('Viewed all movies');
        }
        
        function sortMovies(by) {
            filteredMovies.sort((a, b) => {
                if (by === 'rating') return b.rating - a.rating;
                if (by === 'year') return b.year - a.year;
                return 0;
            });
            displayMovies();
            addToHistory(`Sorted by ${by}`);
            document.getElementById('current-view').textContent = `Sorted by ${by}`;
        }
        
        function showAddMovieModal() {
            currentEditingId = null;
            document.getElementById('modal-title').textContent = 'Add New Movie';
            document.getElementById('movie-form').reset();
            document.getElementById('preview-section').style.display = 'none';
            document.getElementById('movie-modal').classList.add('active');
        }
        
        function editMovie(id, event) {
            event.stopPropagation();
            currentEditingId = id;
            const movie = movies.find(m => m.id === id);
            
            document.getElementById('modal-title').textContent = 'Edit Movie';
            document.getElementById('movie-title').value = movie.title;
            document.getElementById('movie-year').value = movie.year;
            document.getElementById('movie-director').value = movie.director;
            document.getElementById('movie-genre').value = movie.genre;
            document.getElementById('movie-rating').value = movie.rating;
            document.getElementById('movie-description').value = movie.description;
            document.getElementById('preview-section').style.display = 'none';
            
            document.getElementById('movie-modal').classList.add('active');
        }
        
        function closeModal() {
            document.getElementById('movie-modal').classList.remove('active');
        }
        

        function previewMovie() {
            const title = document.getElementById('movie-title').value;
            const year = document.getElementById('movie-year').value;
            const director = document.getElementById('movie-director').value;
            const genre = document.getElementById('movie-genre').value;
            const rating = document.getElementById('movie-rating').value;
            const description = document.getElementById('movie-description').value;
            
            if (!title || !year || !director || !genre || !rating || !description) {
                alert('Please fill in all fields to preview');
                return;
            }
            
            const previewSection = document.getElementById('preview-section');
            const previewContent = document.getElementById('preview-content');
            
            previewContent.innerHTML = `
                <div style="padding: 15px; background: white; border-radius: 8px;">
                    <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 5px;">${title}</div>
                    <div style="color: #666; margin-bottom: 10px;">${year} • ${director}</div>
                    <div style="background: #ffd700; color: #333; padding: 4px 10px; border-radius: 5px; display: inline-block; font-weight: bold; margin-bottom: 10px;">
                        * ${rating}/10
                    </div>
                    <div style="margin-bottom: 10px;"><strong>Genre:</strong> ${genre}</div>
                    <div style="color: #555; line-height: 1.5;">${description}</div>
                </div>
            `;
            
            previewSection.style.display = 'block';
        }
        
        function saveMovie(event) {
            event.preventDefault();
            
            const movieData = {
                id: currentEditingId || Date.now(),
                title: document.getElementById('movie-title').value,
                year: parseInt(document.getElementById('movie-year').value),
                director: document.getElementById('movie-director').value,
                genre: document.getElementById('movie-genre').value,
                rating: parseFloat(document.getElementById('movie-rating').value),
                description: document.getElementById('movie-description').value
            };
            
            const url = currentEditingId ? `/api/movies/${currentEditingId}` : '/api/movies';
            const method = currentEditingId ? 'PUT' : 'POST';
            
            fetch(url, {
                method: method,
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(movieData)
            })
            .then(response => response.json())
            .then(data => {
                loadMovies();
                closeModal();
                addToHistory(currentEditingId ? `Edited "${movieData.title}"` : `Added "${movieData.title}"`);
            });
        }
        
        function deleteMovie(id, event) {
            event.stopPropagation();
            const movie = movies.find(m => m.id === id);
            
            if (!confirm(`Are you sure you want to delete "${movie.title}"?`)) {
                return;
            }
            
            fetch(`/api/movies/${id}`, {method: 'DELETE'})
                .then(() => {
                    addToHistory(`Deleted "${movie.title}"`);
                    loadMovies();
                });
        }
        
    
        function setViewMode(mode) {
            currentViewMode = mode;
            const buttons = document.querySelectorAll('.view-mode-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            const container = document.getElementById('movies-container');
            if (mode === 'list') {
                container.style.gridTemplateColumns = '1fr';
            } else if (mode === 'compact') {
                container.style.gridTemplateColumns = 'repeat(auto-fill, minmax(250px, 1fr))';
            } else {
                container.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
            }
            
            addToHistory(`Changed to ${mode} view`);
        }
        
      
        function addToHistory(action) {

            history = history.slice(0, historyIndex + 1);
            history.push(action);
            historyIndex = history.length - 1;
            updateHistoryUI();
        }
        
        function historyUndo() {
            if (historyIndex > 0) {
                historyIndex--;
                updateHistoryUI();
            }
        }
        
        function historyRedo() {
            if (historyIndex < history.length - 1) {
                historyIndex++;
                updateHistoryUI();
            }
        }
        
        function clearHistory() {
            history = [];
            historyIndex = -1;
            updateHistoryUI();
        }
        
        function updateHistoryUI() {
            const undoBtn = document.getElementById('undo-btn');
            const redoBtn = document.getElementById('redo-btn');
            const historyInfo = document.getElementById('history-info');
            
            undoBtn.disabled = historyIndex <= 0;
            redoBtn.disabled = historyIndex >= history.length - 1;
            
            if (history.length > 0 && historyIndex >= 0) {
                historyInfo.textContent = `Last action: ${history[historyIndex]}`;
            } else {
                historyInfo.textContent = 'No actions yet';
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/movies', methods=['GET'])
def get_movies():
    return jsonify(load_movies())

@app.route('/api/movies', methods=['POST'])
def add_movie():
    movies = load_movies()
    new_movie = request.json
    
    # mak sure id is new
    if not new_movie.get('id'):
        new_movie['id'] = max([m['id'] for m in movies], default=0) + 1
    
    movies.append(new_movie)
    save_movies(movies)
    return jsonify(new_movie), 201

@app.route('/api/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    movies = load_movies()
    updated_movie = request.json
    
    for i, movie in enumerate(movies):
        if movie['id'] == movie_id:
            movies[i] = updated_movie
            save_movies(movies)
            return jsonify(updated_movie)
    
    return jsonify({'error': 'Movie not found'}), 404

@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    movies = load_movies()
    movies = [m for m in movies if m['id'] != movie_id]
    save_movies(movies)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5777)
