<?php
require_once 'includes/db.php';
session_start();

if(!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

if(!isset($_GET['dest_id']) || !is_numeric($_GET['dest_id'])) {
    header("Location: destinations.php");
    exit;
}

$dest_id = $_GET['dest_id'];
$stmt = $pdo->prepare("SELECT * FROM destinations WHERE id = ?");
$stmt->execute([$dest_id]);
$destination = $stmt->fetch();

if(!$destination) {
    header("Location: destinations.php");
    exit;
}

// Get Transport Options
$tStmt = $pdo->query("SELECT * FROM transports");
$transports = $tStmt->fetchAll();

require_once 'includes/header.php';
?>

<div class="container section">
    <div style="max-width: 800px; margin: 0 auto;" class="glass-panel">
        <h2 class="mb-2">Plan Your Complete Trip to <?= htmlspecialchars($destination->name) ?></h2>
        <p class="text-gray-500 mb-4">You are currently booking for <?= htmlspecialchars($destination->name) ?>. Base Price: ₹<?= number_format($destination->base_price) ?>/day.</p>
        
        <form method="POST" action="checkout.php" id="bookingForm">
            <input type="hidden" name="dest_id" value="<?= $destination->id ?>">
            
            <div class="grid grid-cols-2">
                <div class="form-group">
                    <label class="form-label">Full Name</label>
                    <input type="text" class="form-control" value="<?= htmlspecialchars($_SESSION['name']) ?>" readonly style="background: var(--gray-100)">
                </div>
                <div class="form-group">
                    <label class="form-label">Travel Start Date</label>
                    <input type="date" name="start_date" id="startDate" class="form-control" required min="<?= date('Y-m-d') ?>">
                </div>
            </div>

            <div class="grid grid-cols-2">
                <div class="form-group">
                    <label class="form-label">Number of Days</label>
                    <input type="number" name="duration" id="duration" class="form-control" required min="1" max="30" placeholder="E.g. 5">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Trip Start Logic (Duration Handling)</label>
                    <select name="trip_start_mode" class="form-control" required>
                        <option value="Includes Travel">Mode 1: Trip Starts Immediately (Includes Travel)</option>
                        <option value="After Arrival">Mode 2: Trip Starts After Arrival (Adds Travel Day)</option>
                    </select>
                </div>
            </div>

            <div class="form-group mt-2 mb-4">
                <label class="form-label">Select Transport System (Smart Integration)</label>
                <div class="alert alert-info mt-2" id="transportSuggestion" style="display:none;">
                    💡 <strong>Suggestion:</strong> Based on your duration, <span id="sugText"></span> is recommended for an optimal experience!
                </div>
                
                <div class="grid grid-cols-1">
                    <select name="transport_id" id="transportSelect" class="form-control" required>
                        <option value="0">None - Self Arranged (₹0)</option>
                        <?php foreach($transports as $t): ?>
                            <option value="<?= $t->id ?>"><?= htmlspecialchars($t->mode) ?> - <?= htmlspecialchars($t->type) ?> (₹<?= number_format($t->average_cost) ?> est.)</option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>

            <button type="submit" class="btn btn-primary" style="width: 100%; font-size: 1.125rem;">Next: Review Pricing & Checkout</button>
        </form>
    </div>
</div>

<script>
// Smart script that changes recommendation when user enters days
document.getElementById('duration').addEventListener('input', function(e) {
    let days = parseInt(e.target.value);
    let sugBox = document.getElementById('transportSuggestion');
    let sugText = document.getElementById('sugText');
    let transportSelect = document.getElementById('transportSelect');

    if (isNaN(days) || days <= 0) {
        sugBox.style.display = 'none';
        return;
    }

    sugBox.style.display = 'block';

    if (days >= 5) {
        sugText.innerText = "Flight Transport";
        sugBox.className = "alert alert-warning mt-2";
    } else if (days >= 3) {
        sugText.innerText = "Train Transport";
        sugBox.className = "alert alert-success mt-2";
    } else {
        sugText.innerText = "Bus Transport";
        sugBox.className = "alert alert-info mt-2";
    }
});
</script>

<?php require_once 'includes/footer.php'; ?>
