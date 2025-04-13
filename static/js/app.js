class FeelSpeakApp {
    constructor() {
      this.objectUrls = [];
      this.audioContext = null;
      this.analyser = null;
      this.animationId = null;
      this.initElements();
      this.initState();
      this.setupEventListeners();
      this.checkApiStatus();
    }
  
    initElements() {
      this.chatMessages = document.getElementById('chatMessages');
      this.textInput = document.getElementById('textInput');
      this.sendTextBtn = document.getElementById('sendTextBtn');
      this.recordBtn = document.getElementById('recordBtn');
      this.uploadAudioBtn = document.getElementById('uploadAudioBtn');
      this.audioUpload = document.getElementById('audioUpload');
      this.audioVisualizer = document.getElementById('audioVisualizer');
      this.audioWaveform = document.getElementById('audioWaveform');
      this.sendAudioBtn = document.getElementById('sendAudioBtn');
      this.uploadImageBtn = document.getElementById('uploadImageBtn');
      this.imageUpload = document.getElementById('imageUpload');
      this.imagePreviewContainer = document.getElementById('imagePreviewContainer');
      this.imagePreview = document.getElementById('imagePreview');
      this.sendImageBtn = document.getElementById('sendImageBtn');
      this.effectOptions = document.querySelectorAll('.effect-option');
    }
  
    initState() {
      this.currentEffect = 'happy';
      this.audioChunks = [];
      this.mediaRecorder = null;
      this.audioBlob = null;
      this.imageFile = null;
      this.stream = null;
    }
  
    setupEventListeners() {
      // Text input
      this.textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendTextMessage();
        }
      });
      
      this.textInput.addEventListener('input', () => this.adjustTextInputHeight());
      this.sendTextBtn.addEventListener('click', () => this.sendTextMessage());
      
      // Effect selection
      this.effectOptions.forEach(option => {
        option.addEventListener('click', () => this.selectEffect(option));
      });
      
      // Audio handling
      this.uploadAudioBtn.addEventListener('click', () => this.audioUpload.click());
      this.audioUpload.addEventListener('change', (e) => this.handleAudioUpload(e));
      this.recordBtn.addEventListener('mousedown', () => this.startRecording());
      this.recordBtn.addEventListener('mouseup', () => this.stopRecording());
      this.recordBtn.addEventListener('mouseleave', () => this.stopRecording());
      this.sendAudioBtn.addEventListener('click', () => this.sendAudioMessage());
      
      // Image handling
      this.uploadImageBtn.addEventListener('click', () => this.imageUpload.click());
      this.imageUpload.addEventListener('change', (e) => this.handleImageUpload(e));
      this.sendImageBtn.addEventListener('click', () => this.sendImageMessage());
      
      // Cleanup on page unload
      window.addEventListener('beforeunload', () => this.cleanupObjectUrls());
    }
  
    adjustTextInputHeight() {
      this.textInput.style.height = 'auto';
      this.textInput.style.height = `${this.textInput.scrollHeight}px`;
    }
  
    selectEffect(option) {
      this.effectOptions.forEach(opt => opt.classList.remove('active'));
      option.classList.add('active');
      this.currentEffect = option.dataset.effect;
      
      // Add effect indicator to the chat
      const emojiMap = {
        happy: '😊',
        sad: '😢',
        funny: '😂',
        angry: '😠'
      };
      
      this.addMessage(
        `<span class="status-message">Selected mode: ${emojiMap[this.currentEffect]} ${this.currentEffect.charAt(0).toUpperCase() + this.currentEffect.slice(1)}</span>`, 
        'bot', 
        'text'
      );
    }
  
    async checkApiStatus() {
      try {
        const response = await fetch('/api/check');
        if (!response.ok) throw new Error('API not responding');
        const data = await response.json();
        this.addMessage(
          `<span class="status-message">API Status: <span class="status-${data.status}">${data.status}</span></span>`, 
          'bot', 
          'text'
        );
      } catch (error) {
        console.error('API check failed:', error);
        this.addMessage(
          `<span class="error-message">API Connection Error: ${error.message}</span>`, 
          'bot', 
          'text'
        );
      }
    }
  
    async handleAudioUpload(e) {
      if (e.target.files.length > 0) {
        this.audioBlob = e.target.files[0];
        this.audioVisualizer.style.display = 'block';
        this.sendAudioBtn.disabled = false;
        
        // Setup audio visualization
        await this.setupAudioVisualization(this.audioBlob);
        
        this.addMessage(
          '<span class="status-message">Audio file loaded</span>', 
          'bot', 
          'text'
        );
      }
    }
  
    async setupAudioVisualization(blob) {
      try {
        if (!this.audioContext) {
          this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        const arrayBuffer = await blob.arrayBuffer();
        const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
        
        if (!this.analyser) {
          this.analyser = this.audioContext.createAnalyser();
          this.analyser.fftSize = 256;
        }
        
        const source = this.audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(this.analyser);
        this.analyser.connect(this.audioContext.destination);
        
        this.drawAudioVisualization();
        
        // Stop when audio ends
        source.onended = () => {
          cancelAnimationFrame(this.animationId);
          this.clearVisualizer();
        };
        
        source.start(0);
      } catch (error) {
        console.error('Audio visualization error:', error);
      }
    }
  
    drawAudioVisualization() {
      const canvas = this.audioWaveform;
      const ctx = canvas.getContext('2d');
      const width = canvas.width = canvas.offsetWidth;
      const height = canvas.height = canvas.offsetHeight;
      
      const bufferLength = this.analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      const draw = () => {
        this.animationId = requestAnimationFrame(draw);
        this.analyser.getByteFrequencyData(dataArray);
        
        ctx.fillStyle = 'rgb(255, 255, 255)';
        ctx.fillRect(0, 0, width, height);
        
        const barWidth = (width / bufferLength) * 2.5;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
          const barHeight = (dataArray[i] / 255) * height;
          
          // Gradient based on current effect
          let gradient;
          if (this.currentEffect === 'happy') {
            gradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
            gradient.addColorStop(0, '#4cc9f0');
            gradient.addColorStop(1, '#4895ef');
          } else if (this.currentEffect === 'sad') {
            gradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
            gradient.addColorStop(0, '#6c757d');
            gradient.addColorStop(1, '#495057');
          } else if (this.currentEffect === 'angry') {
            gradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
            gradient.addColorStop(0, '#f72585');
            gradient.addColorStop(1, '#b5179e');
          } else { // funny
            gradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
            gradient.addColorStop(0, '#ff9e00');
            gradient.addColorStop(1, '#ff7b00');
          }
          
          ctx.fillStyle = gradient;
          ctx.fillRect(x, height - barHeight, barWidth, barHeight);
          
          x += barWidth + 1;
        }
      };
      
      draw();
    }
  
    clearVisualizer() {
      const canvas = this.audioWaveform;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  
    async startRecording() {
      if (!navigator.mediaDevices || !window.MediaRecorder) {
        this.addMessage(
          '<span class="error-message">Audio recording not supported in this browser</span>', 
          'bot', 
          'text'
        );
        return;
      }
  
      this.audioChunks = [];
      this.audioVisualizer.style.display = 'block';
      this.recordBtn.innerHTML = '<i class="fas fa-stop"></i> Recording...';
      this.recordBtn.classList.add('recording');
      
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Setup audio visualization for live recording
        if (!this.audioContext) {
          this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        
        const source = this.audioContext.createMediaStreamSource(this.stream);
        source.connect(this.analyser);
        
        this.drawAudioVisualization();
        
        this.mediaRecorder = new MediaRecorder(this.stream);
        
        this.mediaRecorder.ondataavailable = e => {
          this.audioChunks.push(e.data);
        };
        
        this.mediaRecorder.onstop = () => {
          this.audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
          this.sendAudioBtn.disabled = false;
          this.addMessage(
            '<span class="status-message">Recording complete</span>', 
            'bot', 
            'text'
          );
          cancelAnimationFrame(this.animationId);
          this.clearVisualizer();
        };
        
        this.mediaRecorder.start();
      } catch (error) {
        console.error('Error accessing microphone:', error);
        this.addMessage(
          '<span class="error-message">Could not access microphone. Please check permissions.</span>', 
          'bot', 
          'text'
        );
        this.recordBtn.innerHTML = '<i class="fas fa-microphone"></i> Record';
        this.recordBtn.classList.remove('recording');
      }
    }
  
    stopRecording() {
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop();
        this.recordBtn.innerHTML = '<i class="fas fa-microphone"></i> Record';
        this.recordBtn.classList.remove('recording');
        
        // Stop all tracks in the stream
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
        }
      }
    }
  
    handleImageUpload(e) {
      if (e.target.files.length > 0) {
        this.imageFile = e.target.files[0];
        const url = URL.createObjectURL(this.imageFile);
        this.objectUrls.push(url);
        this.imagePreview.src = url;
        this.imagePreviewContainer.style.display = 'block';
        this.sendImageBtn.disabled = false;
        
        // Add animation to preview
        this.imagePreview.style.transform = 'scale(0.9)';
        setTimeout(() => {
          this.imagePreview.style.transform = 'scale(1)';
        }, 100);
        
        this.addMessage(
          '<span class="status-message">Image loaded</span>', 
          'bot', 
          'text'
        );
      }
    }
  
    async sendTextMessage() {
      const text = this.textInput.value.trim();
      if (!text) {
        this.addMessage(
          '<span class="error-message">Please enter some text first</span>', 
          'bot', 
          'text'
        );
        return;
      }
      
      this.addMessage(text, 'user', 'text');
      this.textInput.value = '';
      this.textInput.style.height = 'auto';
      
      const processingId = this.addMessage('Processing...', 'bot', 'text', true);
      
      try {
        const response = await fetch('/convert_text', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ 
            text: text, 
            style: this.currentEffect 
          })
        });
  
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to convert text');
        }
        
        this.updateMessage(processingId, data.result, 'bot', 'text');
      } catch (error) {
        console.error('Text conversion error:', error);
        this.updateMessage(
          processingId, 
          `<span class="error-message">${error.message}</span>`, 
          'bot', 
          'text'
        );
      }
    }
  
    async sendAudioMessage() {
      if (!this.audioBlob) {
        this.addMessage(
          '<span class="error-message">No audio to send</span>', 
          'bot', 
          'text'
        );
        return;
      }
      
      this.addMessage('Voice message', 'user', 'audio');
      const processingId = this.addMessage('Processing voice...', 'bot', 'text', true);
      
      try {
        const formData = new FormData();
        formData.append('audio', this.audioBlob, 'recording.wav');
        formData.append('effect', this.currentEffect);
        
        const response = await fetch('/modify_audio', {
          method: 'POST',
          body: formData
        });
  
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || 'Audio processing failed');
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        this.objectUrls.push(url);
        
        // Add mood badge to the message
        const moodBadge = `<span class="mood-badge ${this.currentEffect}">${this.currentEffect}</span>`;
        
        this.updateMessage(processingId, {url, moodBadge}, 'bot', 'audio');
      } catch (error) {
        console.error('Audio processing error:', error);
        this.updateMessage(
          processingId, 
          `<span class="error-message">${error.message}</span>`, 
          'bot', 
          'text'
        );
      } finally {
        this.audioVisualizer.style.display = 'none';
        this.sendAudioBtn.disabled = true;
        this.audioBlob = null;
        cancelAnimationFrame(this.animationId);
        this.clearVisualizer();
      }
    }
  
    async sendImageMessage() {
      if (!this.imageFile) {
        this.addMessage(
          '<span class="error-message">No image to send</span>', 
          'bot', 
          'text'
        );
        return;
      }
      
      const imgUrl = URL.createObjectURL(this.imageFile);
      this.objectUrls.push(imgUrl);
      this.addMessage(imgUrl, 'user', 'image');
      const processingId = this.addMessage('Processing image...', 'bot', 'text', true);
      
      try {
        const formData = new FormData();
        formData.append('image', this.imageFile);
        formData.append('expression', this.currentEffect);
        
        const response = await fetch('/transform_image', {
          method: 'POST',
          body: formData
        });
  
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || 'Image processing failed');
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        this.objectUrls.push(url);
        
        // Add mood badge to the message
        const moodBadge = `<span class="mood-badge ${this.currentEffect}">${this.currentEffect}</span>`;
        
        this.updateMessage(processingId, {url, moodBadge}, 'bot', 'image');
      } catch (error) {
        console.error('Image processing error:', error);
        this.updateMessage(
          processingId, 
          `<span class="error-message">${error.message}</span>`, 
          'bot', 
          'text'
        );
      } finally {
        this.imagePreviewContainer.style.display = 'none';
        this.sendImageBtn.disabled = true;
        this.imageFile = null;
      }
    }
  
    addMessage(content, sender, type, isProcessing = false) {
      const messageDiv = document.createElement('div');
      const messageId = `msg-${Date.now()}`;
      messageDiv.id = messageId;
      messageDiv.className = `message message-${sender} new-message`;
      
      const bubbleDiv = document.createElement('div');
      bubbleDiv.className = `message-bubble ${sender}-bubble`;
      
      const timeSpan = document.createElement('div');
      timeSpan.className = 'message-time';
      const now = new Date();
      timeSpan.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      if (type === 'text') {
        bubbleDiv.innerHTML = content;
      } else if (type === 'audio' && sender === 'user') {
        bubbleDiv.textContent = '🎤 Voice message';
      } else if (type === 'audio' && sender === 'bot') {
        const audioElement = document.createElement('audio');
        audioElement.src = content.url;
        audioElement.controls = true;
        audioElement.className = 'preview-audio';
        bubbleDiv.appendChild(audioElement);
        if (content.moodBadge) {
          bubbleDiv.innerHTML += content.moodBadge;
        }
      } else if (type === 'image') {
        const imgElement = document.createElement('img');
        imgElement.src = content.url || content;
        imgElement.className = 'preview-image';
        bubbleDiv.appendChild(imgElement);
        if (content.moodBadge) {
          bubbleDiv.innerHTML += content.moodBadge;
        }
      }
      
      if (isProcessing) {
        const spinner = document.createElement('div');
        spinner.className = 'processing-spinner';
        bubbleDiv.appendChild(spinner);
        bubbleDiv.classList.add('processing');
      }
      
      messageDiv.appendChild(bubbleDiv);
      messageDiv.appendChild(timeSpan);
      this.chatMessages.appendChild(messageDiv);
      this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
      
      // Remove new-message class after animation completes
      setTimeout(() => {
        messageDiv.classList.remove('new-message');
      }, 300);
      
      return messageId;
    }
  
    updateMessage(id, content, sender, type) {
      const message = document.getElementById(id);
      if (message) {
        const bubble = message.querySelector('.message-bubble');
        bubble.classList.remove('processing');
        bubble.innerHTML = '';
        
        if (type === 'text') {
          bubble.innerHTML = content;
        } else if (type === 'audio') {
          const audioElement = document.createElement('audio');
          audioElement.src = content.url || content;
          audioElement.controls = true;
          audioElement.className = 'preview-audio';
          bubble.appendChild(audioElement);
          if (content.moodBadge) {
            bubble.innerHTML += content.moodBadge;
          }
        } else if (type === 'image') {
          const imgElement = document.createElement('img');
          imgElement.src = content.url || content;
          imgElement.className = 'preview-image';
          bubble.appendChild(imgElement);
          if (content.moodBadge) {
            bubble.innerHTML += content.moodBadge;
          }
        }
        
        // Add animation
        bubble.style.animation = 'none';
        setTimeout(() => {
          bubble.style.animation = 'fadeIn 0.3s ease';
        }, 10);
      }
    }
  
    cleanupObjectUrls() {
      this.objectUrls.forEach(url => URL.revokeObjectURL(url));
      this.objectUrls = [];
      
      // Cleanup audio context
      if (this.audioContext && this.audioContext.state !== 'closed') {
        this.audioContext.close();
      }
      
      // Stop any ongoing visualization
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
      }
    }
  }
  
  // Initialize the app when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    const app = new FeelSpeakApp();
  });