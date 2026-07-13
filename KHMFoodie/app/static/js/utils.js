async function searchRestaurants(keyword) {
    const url = '/api/search/?q=' + encodeURIComponent(keyword);
    const res = await fetch(url);
    if (!res.ok) throw new Error('Search failed: ' + res.status);
    return res.json();
}