import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main App Component
function App() {
  const [topics, setTopics] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [activeView, setActiveView] = useState('home'); // 'home', 'topics', 'search', 'topic-detail'
  
  // AI Chat state
  const [chatMessages, setChatMessages] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [showChat, setShowChat] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchCategories();
    fetchStats();
    fetchTopics();
  }, []);

  const fetchTopics = async (filters = {}) => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (filters.category) params.append('category', filters.category);
      if (filters.difficulty_level) params.append('difficulty_level', filters.difficulty_level);
      if (filters.search) params.append('search', filters.search);
      
      const response = await axios.get(`${API}/topics?${params.toString()}`);
      setTopics(response.data);
    } catch (error) {
      console.error('Error fetching topics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      setLoading(true);
      const params = new URLSearchParams();
      params.append('q', searchQuery);
      if (selectedCategory) params.append('category', selectedCategory);
      if (selectedDifficulty) params.append('difficulty', selectedDifficulty);
      
      const response = await axios.get(`${API}/search?${params.toString()}`);
      setTopics(response.data.results);
      setActiveView('topics');
    } catch (error) {
      console.error('Error searching topics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = () => {
    const filters = {};
    if (selectedCategory) filters.category = selectedCategory;
    if (selectedDifficulty) filters.difficulty_level = selectedDifficulty;
    if (searchQuery) filters.search = searchQuery;
    
    fetchTopics(filters);
    setActiveView('topics');
  };

  const openTopic = async (topicId) => {
    try {
      const response = await axios.get(`${API}/topics/${topicId}`);
      setSelectedTopic(response.data);
      setActiveView('topic-detail');
    } catch (error) {
      console.error('Error fetching topic details:', error);
    }
  };

  // Header Component
  const Header = () => (
    <header className="bg-gradient-to-r from-blue-900 to-blue-700 text-white shadow-lg">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="text-3xl font-bold">🧠</div>
            <div>
              <h1 className="text-2xl font-bold">PsychLearn</h1>
              <p className="text-blue-200 text-sm">Comprehensive Psychology Learning Platform</p>
            </div>
          </div>
          <nav className="hidden md:flex space-x-6">
            <button 
              onClick={() => setActiveView('home')}
              className={`px-4 py-2 rounded-lg transition-colors ${activeView === 'home' ? 'bg-blue-800' : 'hover:bg-blue-800'}`}
            >
              Home
            </button>
            <button 
              onClick={() => setActiveView('topics')}
              className={`px-4 py-2 rounded-lg transition-colors ${activeView === 'topics' ? 'bg-blue-800' : 'hover:bg-blue-800'}`}
            >
              Browse Topics
            </button>
            <button 
              onClick={() => setActiveView('search')}
              className={`px-4 py-2 rounded-lg transition-colors ${activeView === 'search' ? 'bg-blue-800' : 'hover:bg-blue-800'}`}
            >
              Advanced Search
            </button>
          </nav>
        </div>
      </div>
    </header>
  );

  // Hero Section Component
  const HeroSection = () => (
    <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-16">
      <div className="container mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Master Psychology with 
              <span className="text-blue-600"> Comprehensive Learning</span>
            </h2>
            <p className="text-xl text-gray-700 mb-8">
              Explore 150+ high-quality psychology topics across all major fields. 
              From introductory concepts to graduate-level theories, build your expertise with our expertly curated content.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button 
                onClick={() => setActiveView('topics')}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Start Learning
              </button>
              <button 
                onClick={() => setActiveView('search')}
                className="border border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
              >
                Search Topics
              </button>
            </div>
          </div>
          <div className="relative">
            <img 
              src="https://images.unsplash.com/photo-1617791160536-598cf32026fb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwxfHxwc3ljaG9sb2d5JTIwYnJhaW58ZW58MHx8fGJsdWV8MTc1MzQyODQ1OXww&ixlib=rb-4.1.0&q=85"
              alt="Psychology Brain Visualization"
              className="rounded-lg shadow-2xl w-full"
            />
          </div>
        </div>
      </div>
    </section>
  );

  // Stats Section Component
  const StatsSection = () => (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-6">
        <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Comprehensive Psychology Knowledge Base
        </h3>
        {stats && (
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📚</span>
              </div>
              <div className="text-3xl font-bold text-blue-600">{stats.total_topics}</div>
              <div className="text-gray-600">Psychology Topics</div>
            </div>
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🎯</span>
              </div>
              <div className="text-3xl font-bold text-green-600">{stats.total_categories}</div>
              <div className="text-gray-600">Psychology Fields</div>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🧪</span>
              </div>
              <div className="text-3xl font-bold text-purple-600">500+</div>
              <div className="text-gray-600">Research Studies</div>
            </div>
            <div className="text-center">
              <div className="bg-orange-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">👥</span>
              </div>
              <div className="text-3xl font-bold text-orange-600">200+</div>
              <div className="text-gray-600">Famous Psychologists</div>
            </div>
          </div>
        )}
      </div>
    </section>
  );

  // Categories Section Component
  const CategoriesSection = () => (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-6">
        <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Explore Psychology Fields
        </h3>
        <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-6">
          {categories.categories && categories.categories.map((category, index) => (
            <div 
              key={category}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-blue-500"
              onClick={() => {
                setSelectedCategory(category);
                handleFilterChange();
              }}
            >
              <div className="text-2xl mb-3">
                {['🧠', '💭', '👥', '🔬', '🎭', '📊', '🏥', '👶'][index % 8]}
              </div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">{category}</h4>
              <p className="text-gray-600 text-sm">
                {stats?.topics_by_category?.[category] || 0} topics available
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );

  // Search Section Component
  const SearchSection = () => (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-6 max-w-4xl">
        <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Find Your Psychology Topic
        </h3>
        
        <div className="bg-gray-50 p-8 rounded-lg">
          {/* Search Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Topics
            </label>
            <div className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for topics, concepts, psychologists, or experiments..."
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button
                onClick={handleSearch}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Search
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                {categories.categories && categories.categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Level
              </label>
              <select
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Levels</option>
                <option value="introductory">Introductory</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="graduate">Graduate</option>
              </select>
            </div>
          </div>

          <div className="mt-6">
            <button
              onClick={handleFilterChange}
              className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>
    </section>
  );

  // Topics List Component
  const TopicsList = () => (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-6">
        <div className="flex justify-between items-center mb-8">
          <h3 className="text-3xl font-bold text-gray-900">
            Psychology Topics
          </h3>
          <div className="text-sm text-gray-600">
            {topics.length} topics found
          </div>
        </div>
        
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading topics...</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topics.map(topic => (
              <div 
                key={topic.id}
                className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => openTopic(topic.id)}
              >
                <div className="flex justify-between items-start mb-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    topic.difficulty_level === 'introductory' ? 'bg-green-100 text-green-800' :
                    topic.difficulty_level === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    topic.difficulty_level === 'advanced' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {topic.difficulty_level}
                  </span>
                  <span className="text-xs text-gray-500">{topic.reading_time} min read</span>
                </div>
                
                <h4 className="text-xl font-semibold text-gray-900 mb-2">{topic.title}</h4>
                <p className="text-blue-600 text-sm mb-3">{topic.category}</p>
                
                <div className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {topic.content.substring(0, 120)}...
                </div>
                
                {topic.key_concepts.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {topic.key_concepts.slice(0, 3).map(concept => (
                      <span key={concept} className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded">
                        {concept}
                      </span>
                    ))}
                    {topic.key_concepts.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        +{topic.key_concepts.length - 3} more
                      </span>
                    )}
                  </div>
                )}
                
                <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                  Read More →
                </button>
              </div>
            ))}
          </div>
        )}
        
        {!loading && topics.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h4 className="text-xl font-semibold text-gray-900 mb-2">No topics found</h4>
            <p className="text-gray-600">Try adjusting your search criteria or browse our categories.</p>
          </div>
        )}
      </div>
    </section>
  );

  // Topic Detail Component
  const TopicDetail = () => {
    if (!selectedTopic) return null;

    return (
      <section className="py-8 bg-white min-h-screen">
        <div className="container mx-auto px-6 max-w-4xl">
          <button
            onClick={() => setActiveView('topics')}
            className="mb-6 text-blue-600 hover:text-blue-800 flex items-center"
          >
            ← Back to Topics
          </button>
          
          <article className="prose prose-lg max-w-none">
            <div className="mb-8">
              <div className="flex flex-wrap gap-4 mb-4">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  selectedTopic.difficulty_level === 'introductory' ? 'bg-green-100 text-green-800' :
                  selectedTopic.difficulty_level === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                  selectedTopic.difficulty_level === 'advanced' ? 'bg-orange-100 text-orange-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {selectedTopic.difficulty_level}
                </span>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  {selectedTopic.category}
                </span>
                <span className="text-sm text-gray-500">
                  {selectedTopic.reading_time} min read
                </span>
              </div>
              
              <h1 className="text-4xl font-bold text-gray-900 mb-4">{selectedTopic.title}</h1>
              
              {selectedTopic.subcategory && (
                <p className="text-xl text-blue-600 mb-6">{selectedTopic.subcategory}</p>
              )}
            </div>
            
            <div 
              className="prose-content"
              dangerouslySetInnerHTML={{ 
                __html: selectedTopic.content.replace(/\n/g, '<br/>').replace(/#{1,6}\s/g, '<h3>').replace(/<h3>/g, '<h3 class="text-2xl font-bold mt-8 mb-4">') 
              }}
            />
            
            {/* Key Concepts */}
            {selectedTopic.key_concepts.length > 0 && (
              <div className="mt-12 p-6 bg-blue-50 rounded-lg">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Key Concepts</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedTopic.key_concepts.map(concept => (
                    <span key={concept} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                      {concept}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Related Information */}
            <div className="mt-8 grid md:grid-cols-2 gap-6">
              {selectedTopic.psychologists.length > 0 && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">Key Psychologists</h4>
                  <ul className="text-sm text-gray-700">
                    {selectedTopic.psychologists.map(psychologist => (
                      <li key={psychologist}>• {psychologist}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {selectedTopic.experiments.length > 0 && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">Related Experiments</h4>
                  <ul className="text-sm text-gray-700">
                    {selectedTopic.experiments.map(experiment => (
                      <li key={experiment}>• {experiment}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            
            {/* Related Topics */}
            {selectedTopic.related_topics.length > 0 && (
              <div className="mt-8 p-6 bg-green-50 rounded-lg">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Related Topics</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedTopic.related_topics.map(topic => (
                    <span key={topic} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </article>
        </div>
      </section>
    );
  };

  // Footer Component
  const Footer = () => (
    <footer className="bg-gray-900 text-white py-12">
      <div className="container mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-2xl">🧠</span>
              <span className="text-xl font-bold">PsychLearn</span>
            </div>
            <p className="text-gray-400 text-sm">
              Your comprehensive resource for psychology education and research.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Psychology Fields</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>Clinical Psychology</li>
              <li>Cognitive Psychology</li>
              <li>Social Psychology</li>
              <li>Developmental Psychology</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>Research Papers</li>
              <li>Case Studies</li>
              <li>Famous Experiments</li>
              <li>Psychology Timeline</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Features</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>Advanced Search</li>
              <li>Content Filtering</li>
              <li>Reading Progress</li>
              <li>Topic Recommendations</li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 pt-8 mt-8 text-center text-sm text-gray-400">
          <p>&copy; 2025 PsychLearn. Comprehensive Psychology Learning Platform.</p>
        </div>
      </div>
    </footer>
  );

  // Main Render
  return (
    <div className="App min-h-screen bg-gray-50">
      <Header />
      
      {activeView === 'home' && (
        <>
          <HeroSection />
          <StatsSection />
          <CategoriesSection />
        </>
      )}
      
      {activeView === 'search' && <SearchSection />}
      
      {activeView === 'topics' && <TopicsList />}
      
      {activeView === 'topic-detail' && <TopicDetail />}
      
      <Footer />
    </div>
  );
}

export default App;