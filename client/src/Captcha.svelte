<script lang="ts">
  const captchaWidth = '200';
  const captchaHeight = '60';

  let imageContainer = undefined;
  export let captcha = undefined;

  async function getCaptcha() {
    const res = await fetch('__SERVER__/captcha', {
      method: 'get',
      mode: 'cors'
    });
    const data = await res.json();

    if (res.ok) {
      const captchaCanvas = document.createElement('canvas');
      const ctx = captchaCanvas.getContext('2d');

      const image = new Image();
      image.onload = function () {
        ctx.drawImage(image, 0, 0);
      }

      image.alt = 'captcha';
      image.src = `data:image/png;base64,${data.image}`;
      captchaCanvas.setAttribute('aria-label', 'captcha');
      captchaCanvas.setAttribute('role', 'image');
      captchaCanvas.setAttribute('width', captchaWidth);
      captchaCanvas.setAttribute('height', captchaHeight);
      imageContainer.appendChild(captchaCanvas);

      HTMLCanvasElement.prototype.toDataURL = function(type?, encoderOptions?) { return '' }
      HTMLCanvasElement.prototype.toBlob = function(callback, mimeType?, qualityArgument?) { }
    } else {
      throw new Error(data);
    }
  }

  export function refreshCaptcha() {
    captcha = undefined;
    imageContainer.replaceChildren();
    getCaptcha();
  }
</script>

<div class="level">
  <div class="level-left">
    <div bind:this={imageContainer} class="level-item">
    {#await getCaptcha()}
      <p>loading captcha...</p>
    {/await}
    </div>
    <div class="level-item">
      <button on:click|preventDefault={refreshCaptcha} class="button is-warning is-small">
        <span class="icon is-small">
          <i class="fa fa-arrows-rotate"></i>
        </span>
      </button>
    </div>
  </div>
</div>
<input bind:value={captcha} id="captcha-field" class="input" type="text">

<style lang="scss">
</style>
