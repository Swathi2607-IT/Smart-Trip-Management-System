<?php
require_once 'header.php';

// Handle Destination Edit (Weather / Price)
if($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['update_dest'])) {
    $id = (int)$_POST['id'];
    $price = (float)$_POST['base_price'];
    $temp = (int)$_POST['weather_temp'];
    $status = $_POST['weather_status'];
    
    $uStmt = $pdo->prepare("UPDATE destinations SET base_price = ?, weather_temp = ?, weather_status = ? WHERE id = ?");
    $uStmt->execute([$price, $temp, $status, $id]);
    $msg = "Destination parameters successfully updated.";
}

// Fetch destinations
$dStmt = $pdo->query("SELECT * FROM destinations");
$destinations = $dStmt->fetchAll();
?>

<div class="container section">

    <?php if(isset($msg)): ?>
        <div class="alert alert-success"><?= htmlspecialchars($msg) ?></div>
    <?php endif; ?>

    <div style="display: flex; justify-content: space-between; align-items: center;" class="mb-4">
        <h2>Manage Destinations & Live Weather Setup</h2>
    </div>

    <div class="grid grid-cols-2 text-left">
        <?php foreach($destinations as $d): ?>
            <div class="card" style="border: 1px solid var(--gray-200);">
                <img src="<?= htmlspecialchars($d->image_url) ?>" style="height: 150px; object-fit: cover;" alt="">
                <div class="card-body">
                    <h3 class="mb-2"><?= htmlspecialchars($d->name) ?> <span class="badge" style="float: right; font-size: 0.9rem; background: var(--gray-100); color: var(--dark);">₹<?= number_format($d->base_price) ?>/day</span></h3>
                    
                    <form method="POST" action="manage_destinations.php" style="margin-top: 15px;">
                        <input type="hidden" name="id" value="<?= $d->id ?>">
                        
                        <div class="grid grid-cols-2" style="gap: 10px;">
                            <div class="form-group" style="margin-bottom: 10px;">
                                <label class="form-label" style="font-size: 0.8rem;">Base Price (₹/day)</label>
                                <input type="number" name="base_price" class="form-control" value="<?= $d->base_price ?>" required style="padding: 0.5rem;">
                            </div>
                            <div class="form-group" style="margin-bottom: 10px;">
                                <label class="form-label" style="font-size: 0.8rem;">Temp (°C)</label>
                                <input type="number" name="weather_temp" class="form-control" value="<?= $d->weather_temp ?>" required style="padding: 0.5rem;">
                            </div>
                        </div>

                        <div class="form-group" style="margin-bottom: 15px;">
                            <label class="form-label" style="font-size: 0.8rem;">Simulated Weather Status</label>
                            <select name="weather_status" class="form-control" style="padding: 0.5rem;" required>
                                <option value="Sunny" <?= $d->weather_status == 'Sunny' ? 'selected' : '' ?>>Sunny (Ideal)</option>
                                <option value="Cloudy" <?= $d->weather_status == 'Cloudy' ? 'selected' : '' ?>>Cloudy (Good)</option>
                                <option value="Rainy" <?= $d->weather_status == 'Rainy' ? 'selected' : '' ?>>Rainy (Warning)</option>
                                <option value="Stormy" <?= $d->weather_status == 'Stormy' ? 'selected' : '' ?>>Stormy (Danger)</option>
                                <option value="Snowy" <?= $d->weather_status == 'Snowy' ? 'selected' : '' ?>>Snowy (Warning)</option>
                            </select>
                        </div>

                        <button type="submit" name="update_dest" class="btn btn-secondary" style="width: 100%; border: 1px solid var(--gray-200); background: white;">Update Details</button>
                    </form>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
</div>

</main>
</body>
</html>
