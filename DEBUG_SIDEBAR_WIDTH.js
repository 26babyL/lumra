/**
 * SIDEBAR WIDTH DEBUG SCRIPT — Check Computed Styles
 * 
 * Paste ini ke console untuk debug width issue
 */

console.log('='.repeat(70));
console.log('SIDEBAR WIDTH & CLASS DEBUG');
console.log('='.repeat(70));

const sidebarEl = document.getElementById('sidebar');
const bodyEl = document.body;
const mainShellEl = document.querySelector('.app-main-shell');

// 1. Check classes
console.log('\n1. CLASS CHECKS:');
console.log('body.sidebar-open class:', bodyEl.classList.contains('sidebar-open'));
console.log('body classes:', bodyEl.className);

// 2. CSS Variables
console.log('\n2. CSS VARIABLES:');
const style = getComputedStyle(document.documentElement);
console.log('--sidebar-collapsed-width:', style.getPropertyValue('--sidebar-collapsed-width'));
console.log('--sidebar-expanded-width:', style.getPropertyValue('--sidebar-expanded-width'));

// 3. Sidebar computed styles
console.log('\n3. SIDEBAR ELEMENT (.sb):');
if (sidebarEl) {
  const sbComputed = getComputedStyle(sidebarEl);
  console.log('width:', sbComputed.width);
  console.log('transition:', sbComputed.transition);
  console.log('position:', sbComputed.position);
  console.log('Actual innerHTML:', sidebarEl.innerHTML.substring(0, 100) + '...');
} else {
  console.log('❌ Sidebar element NOT FOUND');
}

// 4. App-main-shell computed styles
console.log('\n4. APP-MAIN-SHELL ELEMENT:');
if (mainShellEl) {
  const shellComputed = getComputedStyle(mainShellEl);
  console.log('margin-left:', shellComputed.marginLeft);
  console.log('transition:', shellComputed.transition);
} else {
  console.log('❌ App-main-shell NOT FOUND');
}

// 5. Alpine state check
console.log('\n5. ALPINE STATE:');
if (sidebarEl && sidebarEl.__x && sidebarEl.__x[0]) {
  const component = sidebarEl.__x[0];
  console.log('Alpine open state:', component.$data.open);
  console.log('Alpine mobile state:', component.$data.mobile);
} else {
  console.log('⚠️  Alpine component not attached yet');
}

// 6. Manual toggle test
console.log('\n6. MANUAL TOGGLE TEST:');
console.log('Before toggle:');
console.log('  body.sidebar-open:', bodyEl.classList.contains('sidebar-open'));
console.log('  .sb width:', getComputedStyle(sidebarEl).width);

// Trigger toggle
if (window.toggleSidebarClass) {
  console.log('\nCalling window.toggleSidebarClass()...');
  window.toggleSidebarClass();
  
  // Wait a bit for animation
  setTimeout(() => {
    console.log('\nAfter toggle (after 100ms):');
    console.log('  body.sidebar-open:', bodyEl.classList.contains('sidebar-open'));
    console.log('  .sb width:', getComputedStyle(sidebarEl).width);
    console.log('  transition active:', getComputedStyle(sidebarEl).transition);
    
    // Toggle back
    setTimeout(() => {
      window.toggleSidebarClass();
      console.log('\nToggled back to original state');
    }, 300);
  }, 100);
}

// 7. Summary
console.log('\n' + '='.repeat(70));
console.log('INTERPRETATION:');
console.log('If .sb width is 72px → sidebar NOT expanding (check classes)');
console.log('If .sb width is 260px → sidebar IS expanding ✅');
console.log('='.repeat(70));
