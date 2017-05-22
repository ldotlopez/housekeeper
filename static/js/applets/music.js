'use strict';

class MusicApplet {
	constructor(card) {
		card.innerHTML = 'pedo';
	}
}

window.hk.register('music', MusicApplet);
