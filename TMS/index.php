<?php 
require_once 'includes/header.php'; 
// Fetch 3 popular destinations for highlights
$stmt = $pdo->query("SELECT * FROM destinations LIMIT 3");
$destinations = $stmt->fetchAll();
?>

<div class="hero" style="background-image: url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1600&q=80');">
    <div class="hero-content">
        <h1 class="hero-title">Discover Your Next Great Adventure</h1>
        <p class="hero-subtitle">Smart trip planning, intelligent weather forecasting, and seamless bookings—all in one place.</p>
        <a href="destinations.php" class="btn btn-primary" style="font-size: 1.125rem; padding: 1rem 2rem;">Explore Destinations</a>
    </div>
</div>

<div class="container section">
    <div class="text-center mb-4">
        <h2>Why Choose TMS?</h2>
        <p class="text-gray-500 mt-2">We provide an advanced system that curates the best travel experiences for you.</p>
    </div>

    <div class="grid grid-cols-3">
        <div class="glass-panel text-center">
            <h3 class="mb-2">🌦 Smart Weather UI</h3>
            <p>Our intelligent system warns you about weather disruptions before you book.</p>
        </div>
        <div class="glass-panel text-center">
            <h3 class="mb-2">🗺 Custom Itineraries</h3>
            <p>We generate a precise day-by-day plan with beautiful visuals based on your trip duration.</p>
        </div>
        <div class="glass-panel text-center">
            <h3 class="mb-2">🚗 Smart Transport</h3>
            <p>Select your mode of transit and get dynamic pricing mapped straight into your checkout.</p>
        </div>
    </div>
</div>

<div class="container section">
    <h2 class="mb-4 text-center">Popular Destinations</h2>
    
    <div class="grid grid-cols-3">
        <?php foreach($destinations as $dest): ?>
            <div class="card">
                <img src="<?= htmlspecialchars($dest->image_url) ?>" alt="<?= htmlspecialchars($dest->name) ?>" class="card-img">
                <div class="card-body">
                    <h3 class="card-title"><?= htmlspecialchars($dest->name) ?></h3>
                    <p class="card-text"><?= htmlspecialchars(substr($dest->description, 0, 100)) ?>...</p>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto;">
                        <span style="font-weight: bold; font-size: 1.2rem; color: var(--primary);">₹<?= number_format($dest->base_price) ?></span>
                        <a href="destination_details.php?id=<?= $dest->id ?>" class="btn btn-secondary" style="padding: 0.5rem 1rem;">View Details</a>
                    </div>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
    
    <div class="text-center mt-4">
        <a href="destinations.php" class="btn btn-primary">View All Packages</a>
    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
