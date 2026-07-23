<?php
require_once 'includes/db.php';
session_start();

$error = '';
$success = '';

if($_SERVER['REQUEST_METHOD'] == 'POST') {
    $name = trim($_POST['name']);
    $email = trim($_POST['email']);
    $phone = trim($_POST['phone']);
    $password = password_hash($_POST['password'], PASSWORD_DEFAULT);

    try {
        $stmt = $pdo->prepare("INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, 'user')");
        $stmt->execute([$name, $email, $phone, $password]);
        $success = "Registration successful! You can now <a href='login.php'>Login</a>.";
    } catch (PDOException $e) {
        if($e->getCode() == 23000) {
            $error = "Email already exists!";
        } else {
            $error = "An error occurred. Please try again later.";
        }
    }
}

require_once 'includes/header.php';
?>

<div class="container section">
    <div style="max-width: 400px; margin: 0 auto;">
        <div class="glass-panel text-center">
            <h2 class="mb-2">Create an Account</h2>
            <p class="mb-4 text-gray-500">Join TMS to explore the world.</p>
            
            <?php if($error): ?>
                <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
            <?php endif; ?>
            <?php if($success): ?>
                <div class="alert alert-success"><?= $success ?></div>
            <?php endif; ?>

            <form method="POST" action="register.php" style="text-align: left;">
                <div class="form-group">
                    <label class="form-label">Full Name</label>
                    <input type="text" name="name" class="form-control" required placeholder="John Doe">
                </div>
                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" name="email" class="form-control" required placeholder="john@example.com">
                </div>
                <div class="form-group">
                    <label class="form-label">Phone Number</label>
                    <input type="text" name="phone" class="form-control" required placeholder="(+91)">
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Sign Up</button>
            </form>
            
            <p class="mt-4">Already have an account? <a href="login.php">Log in</a></p>
        </div>
    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
