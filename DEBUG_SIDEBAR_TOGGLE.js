/**
 * SIDEBAR TOGGLE DEBUG SCRIPT
 * 
 * Paste ini ke browser console untuk verify perbaikan bekerja
 * Open DevTools (F12) → Console tab → Paste semua code di bawah → Enter
 */

console.log('='.repeat(70));
console.log('SIDEBAR TOGGLE DEBUG VERIFICATION');
console.log('='.repeat(70));

// 1. Check global toggle function
console.log('\n1. Global Toggle Function:');
if (window.toggleSidebarClass) {
  console.log('✅ window.toggleSidebarClass exists');
} else {
  console.log('❌ window.toggleSidebarClass NOT FOUND');
}

// 2. Check sidebar element
console.log('\n2. Sidebar Element:');
const sidebarEl = document.getElementById('sidebar');
if (sidebarEl) {
  console.log('✅ Sidebar element found (#sidebar)');
  console.log('   Class:', sidebarEl.className);
} else {
  console.log('❌ Sidebar element NOT FOUND');
}

// 3. Check Alpine component
console.log('\n3. Alpine Component:');
if (sidebarEl && sidebarEl.__x && sidebarEl.__x[0]) {
  console.log('✅ Alpine component attached');
  const component = sidebarEl.__x[0];
  if (component.$data && component.$data.open !== undefined) {
    console.log('✅ Alpine state "open" found:', component.$data.open);
  } else {
    console.log('❌ Alpine state "open" NOT FOUND');
  }
} else {
  console.log('⚠️  Alpine component not yet attached (might still be loading)');
}

// 4. Check event listeners
console.log('\n4. Event Listeners:');
const testEvent = new Event('test-toggle');
let globalListenerCaught = false;
const testHandler = () => { globalListenerCaught = true; };
window.addEventListener('toggle-sidebar', testHandler);
window.dispatchEvent(testEvent);
window.removeEventListener('toggle-sidebar', testHandler);
if (globalListenerCaught) {
  console.log('✅ Global event listener working');
} else {
  console.log('❌ Global event listener NOT working');
}

// 5. Check current state
console.log('\n5. Current State:');
console.log('Body classes:', document.body.className);
console.log('sidebar-open class:', document.body.classList.contains('sidebar-open'));
console.log('localStorage sidebarOpen:', localStorage.getItem('sidebarOpen'));

// 6. Test toggle function
console.log('\n6. Test Toggle:');
console.log('Current state before:', document.body.classList.contains('sidebar-open'));
if (window.toggleSidebarClass) {
  window.toggleSidebarClass();
  console.log('Called window.toggleSidebarClass()');
  console.log('Current state after:', document.body.classList.contains('sidebar-open'));
  // Toggle back
  window.toggleSidebarClass();
  console.log('Toggled back. Final state:', document.body.classList.contains('sidebar-open'));
}

// 7. Summary
console.log('\n' + '='.repeat(70));
console.log('SUMMARY: Check berapa item yang ✅ ada');
console.log('Jika semua ✅, sidebar toggle seharusnya berfungsi normal');
console.log('='.repeat(70));

// Bonus: Manual toggle button
console.log('\n7. Quick Toggle Command:');
console.log('Paste ini untuk toggle sidebar: window.toggleSidebarClass()');
