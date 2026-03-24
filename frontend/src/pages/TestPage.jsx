import React from 'react';

export default function TestPage() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>测试页面</h1>
      <p>如果你能看到这个页面，说明React正在工作！</p>
      <button onClick={() => alert('按钮点击正常！')}>
        点击测试
      </button>
    </div>
  );
}
