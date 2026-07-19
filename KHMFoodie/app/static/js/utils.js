async function searchRestaurants(keyword) {
    const url = '/api/search/?q=' + encodeURIComponent(keyword);
    const res = await fetch(url);
    if (!res.ok) throw new Error('Search failed: ' + res.status);
    return res.json();
}

function goToRestaurantDetail(id) {
    console.log("Navigating to restaurant detail for id:", id);
    window.location.href = `/restaurants/${id}`;
}