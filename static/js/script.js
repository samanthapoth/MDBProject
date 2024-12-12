function showSearchOptions() {
    const searchType = document.getElementById('searchType').value;
    document.getElementById('textSearch').style.display = 
        searchType === 'posts' ? 'block' : 'none';
    document.getElementById('genderSearch').style.display = 
        searchType === 'posts_by_gender' ? 'block' : 'none';
    document.getElementById('bloggerSearch').style.display = 
        (searchType === 'posts_by_blogger' || searchType === 'recommendations') ? 'block' : 'none';
}

async function performSearch() {
    const searchType = document.getElementById('searchType').value;
    const resultsDiv = document.getElementById('results');
    
    let requestData = {
        search_type: searchType
    };

    if (searchType === 'posts') {
        requestData.search_text = document.getElementById('textInput').value;
        console.log('Searching for:', requestData.search_text);  // Debug log
    } else if (searchType === 'posts_by_gender') {
        requestData.gender = document.getElementById('genderInput').value;
    } else if (searchType === 'posts_by_blogger' || searchType === 'recommendations') {
        requestData.blogger_id = document.getElementById('bloggerInput').value;
    }

    try {
        console.log('Sending request:', requestData);  // Debug log
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        console.log('Received response:', data);  // Debug log
        
        if (data.success) {
            if (data.data && data.data.length > 0 && data.data[0] !== "No matching posts found") {
                const resultsList = data.data.map(post => `
                    <li class="post-item">
                        <div class="post-metadata">
                            <p><strong>Author:</strong> Blogger ${post.author.blogger_id}</p>
                            <p><strong>Date:</strong> ${post.date}</p>
                            <p><strong>Demographics:</strong> 
                                ${post.author.gender}, 
                                ${post.author.age} years old, 
                                ${post.author.industry}, 
                                ${post.author.sign}
                            </p>
                        </div>
                        <div class="post-content">
                            ${post.content}
                        </div>
                    </li>
                `).join('');
                resultsDiv.innerHTML = `<ul class="posts-list">${resultsList}</ul>`;
            } else {
                resultsDiv.innerHTML = '<p>No results found</p>';
            }
        } else {
            resultsDiv.innerHTML = `<p class="error">Error: ${data.error}</p>`;
        }
    } catch (error) {
        console.error('Search error:', error);  // Debug log
        resultsDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Add event listener for search type changes
document.addEventListener('DOMContentLoaded', function() {
    const searchTypeSelect = document.getElementById('searchType');
    searchTypeSelect.addEventListener('change', showSearchOptions);
    showSearchOptions(); // Initial setup
}); 