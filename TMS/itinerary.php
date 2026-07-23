<?php
require_once 'includes/db.php';
session_start();

if(!isset($_GET['booking_id'])) {
    header("Location: my_bookings.php");
    exit;
}

$booking_id = (int)$_GET['booking_id'];
$stmt = $pdo->prepare("SELECT * FROM bookings WHERE id = ?");
$stmt->execute([$booking_id]);
$booking = $stmt->fetch();

if(!$booking || ($_SESSION['role'] !== 'admin' && $_SESSION['user_id'] != $booking->user_id)) {
    die("Unauthorized.");
}

$pStmt = $pdo->prepare("SELECT * FROM places WHERE destination_id = ?");
$pStmt->execute([$booking->destination_id]);
$places = $pStmt->fetchAll();

// Dynamic Engine to split Places across Days
$duration = $booking->duration;
$places_count = count($places);
$places_per_day = max(1, ceil($places_count / $duration));

$itinerary = [];
$place_index = 0;

for($i = 1; $i <= $duration; $i++) {
    $day_places = [];
    for($j = 0; $j < $places_per_day; $j++) {
        if($place_index < $places_count) {
            $day_places[] = $places[$place_index];
            $place_index++;
        }
    }
    // If we run out of places but still have days, give them a 'Leisure Day'
    if(empty($day_places)) {
        $day_places[] = (object)[
            'name' => 'Leisure & Reflection',
            'category' => 'Relaxation',
            'image_url' => 'https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=800&q=80',
            'is_leisure' => true
        ];
    }
    $itinerary[$i] = $day_places;
}

require_once 'includes/header.php';
?>

<div class="hero" style="height: 30vh; background: var(--dark);">
    <div class="hero-content">
        <h1 class="hero-title">Your Visual Travel Plan</h1>
        <p class="hero-subtitle">Day-by-Day Customized Experience Generator</p>
    </div>
</div>

<div class="container section">

    <?php if($booking->status == 'Cancelled'): ?>
        <div class="alert alert-danger text-center">
            ⚠️ This booking has been cancelled. This itinerary is no longer active.
        </div>
    <?php endif; ?>

    <div style="max-width: 800px; margin: 0 auto;">
        
        <?php foreach($itinerary as $day => $plz): ?>
            <div class="itinerary-day text-left">
                <h3 style="color: var(--primary); margin-bottom: 1rem;">Day <?= $day ?> 
                    <span style="color: var(--gray-500); font-size: 1rem; font-weight: normal;"> - <?= date('d M Y', strtotime($booking->start_date . " + " . ($day - 1) . " days")) ?></span>
                </h3>
                
                <div class="grid grid-cols-2">
                    <?php foreach($plz as $p): ?>
                        <div class="glass-panel" style="padding: 1rem; background-image: linear-gradient(rgba(255,255,255,0.9), rgba(255,255,255,0.8)), url('<?= htmlspecialchars($p->image_url) ?>'); background-size: cover;">
                            <h4 style="margin: 0; color: var(--dark);"><?= htmlspecialchars($p->name) ?></h4>
                            <p style="font-size: 0.875rem; color: var(--gray-500);"><?= isset($p->category) ? $p->category : 'Activity' ?></p>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        <?php endforeach; ?>

        <div class="text-center mt-4">
            <a href="my_bookings.php" class="btn btn-secondary">Return to Dashboard</a>
        </div>
    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
