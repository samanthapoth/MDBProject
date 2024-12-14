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
    console.log("Starting search...");
    const searchType = document.getElementById('searchType').value;
    const resultsDiv = document.getElementById('results');
    
    let requestData = {
        search_type: searchType
    };

    if (searchType === 'posts') {
        requestData.search_text = document.getElementById('textInput').value;
        console.log('Searching for:', requestData.search_text);
    } else if (searchType === 'posts_by_gender') {
        requestData.gender = document.getElementById('genderInput').value;
    } else if (searchType === 'posts_by_blogger' || searchType === 'recommendations') {
        const bloggerId = document.getElementById('bloggerInput').value;
        if (!bloggerId) {
            resultsDiv.innerHTML = '<p class="error">Error: Blogger ID is required</p>';
            return;
        }
        requestData.blogger_id = bloggerId;
        console.log('Searching for blogger ID:', bloggerId);
    }

    try {
        console.log('Sending request:', requestData);
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        console.log('Received response:', data);
        
        if (data.success) {
            if (data.data && data.data.length > 0) {
                let resultsList;
                
                if (searchType === 'recommendations') {
                    // Format recommendations without post content
                    resultsList = data.data.map(post => {
                        console.log("Processing post:", post);  // Debug print
                        return `
                            <li class="post-item">
                                <div class="post-metadata">
                                    <p><strong>Author:</strong> Blogger ${post.author}</p>
                                    <p><strong>Demographics:</strong> ${post.demographics}</p>
                                </div>
                            </li>
                        `;
                    }).join('');
                    console.log("Final HTML:", resultsList);  // Debug print
                } else {
                    // Regular post handling for other search types
                    resultsList = data.data.map(post => {
                        if (!post || !post.author) {
                            console.error('Invalid post data:', post);
                            return '';
                        }

                        let formattedDate = 'No date available';
                        if (post.date) {
                            try {
                                const dateStr = post.date.replace(/,/g, ' ');
                                const parts = dateStr.trim().split(/\s+/);
                                if (parts.length === 3) {
                                    const [day, month, year] = parts;
                                    formattedDate = `${month} ${day} ${year}`;
                                } else {
                                    formattedDate = post.date;
                                }
                            } catch (e) {
                                console.error("Date parsing error:", e);
                                formattedDate = post.date;
                            }
                        }

                        return `
                            <li class="post-item">
                                <div class="post-metadata">
                                    <p><strong>Author:</strong> Blogger ${post.author.blogger_id}</p>
                                    <p><strong>Date:</strong> ${formattedDate}</p>
                                    <p><strong>Demographics:</strong> 
                                        ${post.author.gender || 'Unknown'}, 
                                        ${post.author.age || 'Unknown'} years old, 
                                        ${post.author.industry || 'Unknown'}, 
                                        ${post.author.sign || 'Unknown'}
                                    </p>
                                </div>
                                <div class="post-content">
                                    ${post.content || 'No content available'}
                                </div>
                            </li>
                        `;
                    }).filter(item => item).join('');
                }
                
                if (resultsList) {
                    resultsDiv.innerHTML = `<ul class="posts-list">${resultsList}</ul>`;
                } else {
                    resultsDiv.innerHTML = '<p>No valid results found</p>';
                }
            } else {
                resultsDiv.innerHTML = '<p>No results found</p>';
            }
        } else {
            resultsDiv.innerHTML = `<p class="error">Error: ${data.error || 'Unknown error occurred'}</p>`;
        }
    } catch (error) {
        console.error('Search error:', error);
        resultsDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("Page loaded and script initialized");
    const searchTypeSelect = document.getElementById('searchType');
    searchTypeSelect.addEventListener('change', showSearchOptions);
    showSearchOptions();
});