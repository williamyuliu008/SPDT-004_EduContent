// 4 步法训练系统 MVP - 前端交互
// 验收模式：填空验证

(function() {
  const form = document.getElementById('verify-form');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    const userInput = document.getElementById('user-input').value.trim();
    const expected = document.querySelector('.expected').dataset.expected.trim();
    const result = document.getElementById('result');

    // 简单字符串匹配（容忍空白差异）
    const normalize = (s) => s.replace(/\s+/g, '').replace(/，/g, ',').replace(/。/g, '.');
    const isCorrect = normalize(userInput) === normalize(expected);

    if (isCorrect) {
      result.className = 'correct';
      result.textContent = '✓ 正确！答案匹配。';
    } else {
      result.className = 'wrong';
      result.innerHTML = `✗ 不匹配。<br>你的答案: <code>${userInput}</code><br>参考答案: <code>${expected}</code><br>请查看下方"易混淆辨析"后重试。`;
    }
  });
})();
