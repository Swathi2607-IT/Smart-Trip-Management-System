<?php
require_once 'includes/db.php';
require_once 'includes/header.php';

$stmt = $pdo->query("SELECT * FROM destinations ORDER BY id DESC");
$allDestinations = $stmt->fetchAll();
?>

<div class="hero" style="height: 40vh; min-height: 250px; background-image: url('https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1600&q=80');">
    <div class="hero-content">
        <h1 class="hero-title">Explore All Destinations</h1>
        <p class="hero-subtitle">Handpicked locations for your ultimate getaway.</p>
    </div>
</div>

<div class="container section">
    <div class="grid grid-cols-3">
        <?php foreach($allDestinations as $dest): ?>
            <div class="card">
                <img src="<?= htmlspecialchars($dest->image_url) ?>" alt="<?= htmlspecialchars($dest->name) ?>" class="card-img">
                <div class="card-body">
                    <h3 class="card-title"><?= htmlspecialchars($dest->name) ?></h3>
                    <p class="card-text"><?= htmlspecialchars(substr($dest->description, 0, 100)) ?>...</p>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto;">
                        <span style="font-weight: bold; font-size: 1.2rem; color: var(--primary);">₹<?= number_format($dest->base_price) ?> / day</span>
                        <a href="destination_details.php?id=<?= $dest->id ?>" class="btn btn-secondary" style="padding: 0.5rem 1rem;">View Package</a>
                    </div>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
