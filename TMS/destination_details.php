<?php
require_once 'includes/db.php';

if(!isset($_GET['id']) || !is_numeric($_GET['id'])) {
    header("Location: destinations.php");
    exit;
}

$dest_id = $_GET['id'];
$stmt = $pdo->prepare("SELECT * FROM destinations WHERE id = ?");
$stmt->execute([$dest_id]);
$destination = $stmt->fetch();

if(!$destination) {
    header("Location: destinations.php");
    exit;
}

// Simulated Smart Recognition for Weather
$weatherWarnings = ['Rainy', 'Stormy', 'Snowy'];
$isBadWeather = in_array($destination->weather_status, $weatherWarnings);
$badgeClass = 'badge-sunny';

if($destination->weather_status === 'Rainy') $badgeClass = 'badge-rainy';
if($destination->weather_status === 'Cloudy') $badgeClass = 'badge-cloudy';
if($destination->weather_status === 'Stormy') $badgeClass = 'badge-stormy';

require_once 'includes/header.php';
?>

<div class="hero" style="height: 50vh; background-image: url('<?= htmlspecialchars($destination->image_url) ?>');">
    <div class="hero-content">
        <h1 class="hero-title"><?= htmlspecialchars($destination->name) ?></h1>
    </div>
</div>

<div class="container section">
    
    <?php if($isBadWeather): ?>
        <div class="alert alert-danger" style="display: flex; align-items: center; gap: 10px;">
            ⚠️ <strong>WEATHER ALERT:</strong> It is currently <?= strtolower($destination->weather_status) ?> in <?= htmlspecialchars($destination->name) ?>. Travel is not recommended, consider rescheduling your trip!
        </div>
    <?php else: ?>
        <div class="alert alert-success" style="display: flex; align-items: center; gap: 10px;">
            ✅ <strong>SMART SUGGESTION:</strong> The weather is <?= strtolower($destination->weather_status) ?> and <?= $destination->weather_temp ?>°C. It is an ideal condition for travel and outdoor activities.
        </div>
    <?php endif; ?>

    <div class="grid" style="grid-template-columns: 2fr 1fr; gap: 2rem;">
        <div>
            <h2>About <?= htmlspecialchars($destination->name) ?></h2>
            <p class="mt-2 text-gray-500" style="line-height:1.8; font-size: 1.1rem;"><?= nl2br(htmlspecialchars($destination->description)) ?></p>
            
            <h3 class="mt-4 mb-2">Popular Attractions Included</h3>
            <div class="grid grid-cols-2 mt-2">
                <?php
                $pStmt = $pdo->prepare("SELECT * FROM places WHERE destination_id = ?");
                $pStmt->execute([$dest_id]);
                $places = $pStmt->fetchAll();
                
                foreach($places as $place): ?>
                    <div style="display: flex; align-items: center; gap: 10px; background: white; padding: 10px; border-radius: 8px; box-shadow: var(--shadow-sm);">
                        <img src="<?= htmlspecialchars($place->image_url) ?>" style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover;">
                        <div>
                            <strong><?= htmlspecialchars($place->name) ?></strong><br>
                            <span style="font-size: 0.8rem; color: var(--gray-500);"><?= $place->category ?></span>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>

        <div>
            <div class="glass-panel" style="position: sticky; top: 100px;">
                <h3 class="mb-2">Trip Summary</h3>
                <div style="font-size: 2rem; font-weight: bold; color: var(--primary); margin-bottom: 1rem;">
                    ₹<?= number_format($destination->base_price) ?> <span style="font-size: 1rem; color: var(--gray-500);">/ per day base package</span>
                </div>
                
                <div class="mb-3" style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--gray-200); padding-bottom: 10px;">
                    <span class="text-gray-500">Current Temp:</span>
                    <strong><?= $destination->weather_temp ?>°C</strong>
                </div>
                
                <div class="mb-4" style="display: flex; justify-content: space-between;">
                    <span class="text-gray-500">Condition:</span>
                    <span class="badge <?= $badgeClass ?>"><?= htmlspecialchars($destination->weather_status) ?></span>
                </div>

                <?php if(isset($_SESSION['user_id'])): ?>
                    <form method="GET" action="book.php">
                        <input type="hidden" name="dest_id" value="<?= $destination->id ?>">
                        <button type="submit" class="btn btn-primary" style="width: 100%; font-size: 1.1rem;">Plan Your Trip Now</button>
                    </form>
                <?php else: ?>
                    <a href="login.php" class="btn btn-primary" style="display: block; width: 100%;">Login to Book This Trip</a>
                <?php endif; ?>
            </div>
        </div>
    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
