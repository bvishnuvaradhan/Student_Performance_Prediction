document.querySelector('form').addEventListener('submit', function() {
    const btn = document.querySelector('button');
    btn.innerHTML = '🤖 AI is Analyzing...';
    btn.style.opacity = '0.7';
    btn.style.cursor = 'not-allowed';
});

// Optional: Add a simple fade-in effect when the page loads
document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.glass-card').style.opacity = '0';
    setTimeout(() => {
        document.querySelector('.glass-card').style.transition = 'opacity 1s ease-in';
        document.querySelector('.glass-card').style.opacity = '1';
    }, 100);
});