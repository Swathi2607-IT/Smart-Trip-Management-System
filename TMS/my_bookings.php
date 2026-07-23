<?php
require_once 'includes/db.php';
session_start();

if(!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

$user_id = $_SESSION['user_id'];
$stmt = $pdo->prepare("
    SELECT b.*, d.name as dest_name, d.image_url
    FROM bookings b
    JOIN destinations d ON b.destination_id = d.id
    WHERE b.user_id = ?
    ORDER BY b.id DESC
");
$stmt->execute([$user_id]);
$bookings = $stmt->fetchAll();

require_once 'includes/header.php';
?>

<div class="hero" style="height: 30vh; background-image: url('https://images.unsplash.com/photo-1503220317375-aaad61436b1b?w=1600&q=80');">
    <div class="hero-content">
        <h1 class="hero-title">My Bookings</h1>
        <p class="hero-subtitle">Manage, track, and review your current travel plans.</p>
    </div>
</div>

<div class="container section">

    <?php if(isset($_GET['msg'])): ?>
        <div class="alert alert-success">
            <?= htmlspecialchars($_GET['msg']) ?>
        </div>
    <?php endif; ?>

    <?php if(count($bookings) === 0): ?>
        <div class="text-center glass-panel" style="padding: 4rem 2rem;">
            <p class="text-gray-500 mb-4 text-center">You haven't booked any trips yet.</p>
            <a href="destinations.php" class="btn btn-primary">Browse Packages</a>
        </div>
    <?php else: ?>
        <div class="grid grid-cols-1">
            <?php foreach($bookings as $b): ?>
                <div class="card" style="flex-direction: row; align-items: stretch; border: 1px solid var(--gray-200);">
                    <img src="<?= htmlspecialchars($b->image_url) ?>" style="width: 250px; object-fit: cover;" class="card-img" alt="">
                    
                    <div class="card-body" style="flex-direction: row; justify-content: space-between;">
                        <div>
                            <h3 class="card-title"><?= htmlspecialchars($b->dest_name) ?> <span class="badge status-<?= strtolower($b->status) ?>" style="font-size: 0.8rem; margin-left: 10px;"><?= htmlspecialchars($b->status) ?></span></h3>
                            <p class="card-text mb-2">
                                <strong>Date:</strong> <?= date('d M Y', strtotime($b->start_date)) ?> to <?= date('d M Y', strtotime($b->end_date)) ?> (<?= $b->duration ?> Days)<br>
                                <strong>Logic:</strong> <?= htmlspecialchars($b->trip_start_mode) ?><br>
                                <strong>Cost:</strong> ₹<?= number_format($b->total_cost) ?>
                            </p>
                            
                            <?php if($b->status === 'Cancelled'): ?>
                                <p style="color: var(--error); font-weight: bold;">
                                    Refunded Amount: ₹<?= number_format($b->refund_amount) ?>
                                </p>
                            <?php endif; ?>
                        </div>
                        
                        <div style="display: flex; flex-direction: column; gap: 10px; justify-content: center;">
                            <?php if($b->status === 'Pending'): ?>
                                <form action="payment.php" method="POST">
                                    <input type="hidden" name="booking_id" value="<?= $b->id ?>">
                                    <button class="btn btn-primary" style="width: 100%;">Pay Now</button>
                                </form>
                            <?php elseif($b->status === 'Confirmed'): ?>
                                <a href="receipt.php?token=<?= htmlspecialchars($b->receipt_token) ?>" class="btn btn-primary">View Receipt</a>
                                <a href="itinerary.php?booking_id=<?= $b->id ?>" class="btn btn-secondary">Itinerary</a>
                                
                                <!-- Cancel Logic -->
                                <?php 
                                    $today = new DateTime();
                                    $tripStart = new DateTime($b->start_date);
                                    if($today < $tripStart): 
                                ?>
                                    <a href="cancel_booking.php?id=<?= $b->id ?>" class="btn btn-danger text-center">Cancel Trip</a>
                                <?php endif; ?>
                                
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</div>

<?php require_once 'includes/footer.php'; ?>
