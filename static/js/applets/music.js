'use strict';

class MusicApplet {
	constructor(card) {
		card.content.innerHTML = 'pedo';
	}
}

window.hk.register('music', MusicApplet);
